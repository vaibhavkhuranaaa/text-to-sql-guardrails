from __future__ import annotations

from dataclasses import dataclass

import duckdb
import sqlglot
from sqlglot import exp

from .db import SCHEMA

ROW_LIMIT = 100
BLOCKED_FUNCTIONS = {"read_csv", "read_parquet", "read_json", "http_get", "shell"}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    checks: list[str]
    reason: str | None = None
    sql: str | None = None


def validate(sql: str, connection: duckdb.DuckDBPyConnection) -> ValidationResult:
    checks: list[str] = []
    try:
        parsed = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError:
        return ValidationResult(False, checks, "Malformed SQL was rejected before execution.")
    if len(parsed) != 1 or not isinstance(parsed[0], exp.Select):
        return ValidationResult(False, checks, "Only one SELECT statement is permitted.")
    expression = parsed[0]
    checks.append("single_select")
    tables = {table.name for table in expression.find_all(exp.Table)}
    if not tables <= set(SCHEMA):
        return ValidationResult(
            False, checks, f"Unknown or disallowed table: {sorted(tables - set(SCHEMA))}."
        )
    checks.append("allowed_tables")
    aliases = {table.alias_or_name: table.name for table in expression.find_all(exp.Table)}
    projection_aliases = {
        alias.alias for alias in expression.expressions if isinstance(alias, exp.Alias)
    }
    for column in expression.find_all(exp.Column):
        if not column.table and column.name in projection_aliases:
            continue
        if column.name == "*":
            continue
        candidates = [aliases.get(column.table)] if column.table else list(tables)
        if not any(candidate and column.name in SCHEMA[candidate] for candidate in candidates):
            return ValidationResult(False, checks, f"Unknown or disallowed column: {column.sql()}.")
    checks.append("allowed_columns")
    for function in expression.find_all(exp.Func):
        if function.sql_name().lower() in BLOCKED_FUNCTIONS:
            return ValidationResult(
                False, checks, f"Unsafe function is not permitted: {function.sql_name()}."
            )
    checks.append("safe_functions")
    guarded_sql = f"{expression.sql(dialect='duckdb')} LIMIT {ROW_LIMIT}"
    try:
        connection.execute(f"EXPLAIN {guarded_sql}")
    except duckdb.Error as exc:
        return ValidationResult(False, checks, f"Schema verification failed: {exc}.")
    checks.extend(["schema_verified", "explain_passed", f"row_limit_{ROW_LIMIT}"])
    return ValidationResult(True, checks, sql=guarded_sql)

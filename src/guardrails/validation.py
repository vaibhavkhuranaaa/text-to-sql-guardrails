from __future__ import annotations

from dataclasses import asdict, dataclass

import duckdb
import sqlglot
from sqlglot import exp

from .db import DEMO_SCHEMA, IDENTIFIER_COLUMNS, policy_schema, prepared_read_only_connection

ROW_LIMIT = 100
MAX_SQL_LENGTH = 12_000
MAX_AST_NODES = 400
BLOCKED_WORDS = {
    "attach",
    "call",
    "copy",
    "create",
    "delete",
    "drop",
    "execute",
    "export",
    "insert",
    "install",
    "load",
    "merge",
    "pragma",
    "replace",
    "update",
    "vacuum",
    "alter",
}
BLOCKED_FUNCTIONS = {
    "read_csv",
    "read_parquet",
    "read_json",
    "read_json_auto",
    "http_get",
    "shell",
    "query_table",
}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    checks: list[str]
    reason: str | None = None
    sql: str | None = None
    referenced_tables: list[str] | None = None
    referenced_columns: list[str] | None = None
    explain_summary: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def validate_sql(
    sql: str,
    connection: duckdb.DuckDBPyConnection | None = None,
    schema: dict[str, set[str]] | None = None,
) -> ValidationResult:
    checks: list[str] = []
    schema = schema or policy_schema()
    if not sql.strip() or len(sql) > MAX_SQL_LENGTH:
        return ValidationResult(False, checks, "SQL is empty or exceeds the policy size limit.")
    try:
        parsed = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError:
        return ValidationResult(False, checks, "Malformed SQL was rejected before execution.")
    if len(parsed) != 1:
        return ValidationResult(False, checks, "Only one read-only statement is permitted.")
    expression = parsed[0]
    if not isinstance(expression, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        return ValidationResult(
            False, checks, "Only read-only SELECT, CTE, or set-operation queries are permitted."
        )
    checks.append("single_read_only_statement")
    if sum(1 for _ in expression.walk()) > MAX_AST_NODES:
        return ValidationResult(False, checks, "Query exceeds the AST complexity limit.")
    if any(
        isinstance(node, (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Command))
        for node in expression.walk()
    ):
        return ValidationResult(
            False, checks, "DDL, DML, and command statements are not permitted."
        )
    if any(
        any(isinstance(item, exp.Star) for item in select.expressions)
        for select in expression.find_all(exp.Select)
    ):
        return ValidationResult(
            False, checks, "SELECT * is not permitted because it could disclose excluded fields."
        )
    checks.extend(["complexity_bounded", "no_ddl_dml"])
    cte_names = {cte.alias_or_name for cte in expression.find_all(exp.CTE)}
    tables = {table.name for table in expression.find_all(exp.Table) if table.name not in cte_names}
    if not tables <= set(schema):
        return ValidationResult(
            False, checks, f"Unknown or disallowed table: {sorted(tables - set(schema))}."
        )
    checks.append("allowed_tables")
    aliases = {
        table.alias_or_name: table.name
        for table in expression.find_all(exp.Table)
        if table.name in schema
    }
    visible_columns: set[str] = set()
    for column in expression.find_all(exp.Column):
        if column.name == "*":
            return ValidationResult(
                False,
                checks,
                "SELECT * is not permitted because it could disclose excluded fields.",
            )
        if column.table and column.table in aliases:
            source = aliases[column.table]
            if column.name not in schema[source]:
                return ValidationResult(
                    False, checks, f"Unknown or disallowed column: {column.sql()}."
                )
            if column.name in IDENTIFIER_COLUMNS and not _is_join_key(column):
                return ValidationResult(
                    False, checks, "Identifier-like fields are excluded from the curated model."
                )
            if column.name not in IDENTIFIER_COLUMNS:
                visible_columns.add(f"{source}.{column.name}")
        elif not column.table:
            # Unqualified names are allowed only when known in one physical table or CTE output.
            matching = [table for table in tables if column.name in schema[table]]
            if not matching and column.name not in _projection_aliases(expression):
                # CTE columns are checked by EXPLAIN, which also handles derived aliases.
                continue
            if matching and column.name in IDENTIFIER_COLUMNS and not _is_join_key(column):
                return ValidationResult(
                    False, checks, "Identifier-like fields are excluded from the curated model."
                )
            if matching and column.name not in IDENTIFIER_COLUMNS:
                visible_columns.add(f"{matching[0]}.{column.name}")
    checks.append("curated_columns")
    for function in expression.find_all(exp.Func):
        if function.sql_name().lower() in BLOCKED_FUNCTIONS:
            return ValidationResult(
                False, checks, f"Unsafe function is not permitted: {function.sql_name()}."
            )
    checks.append("safe_functions")
    ranking_functions = (exp.Rank, exp.DenseRank, exp.RowNumber)
    if any(
        isinstance(window.this, ranking_functions) and window.args.get("order") is None
        for window in expression.find_all(exp.Window)
    ):
        return ValidationResult(
            False,
            checks,
            "Ranking window functions require an explicit ORDER BY for reviewable semantics.",
        )
    if any(
        isinstance(window.this, ranking_functions) for window in expression.find_all(exp.Window)
    ):
        checks.append("ranking_order_explicit")
    rendered = expression.sql(dialect="duckdb")
    guarded_sql = rendered if _has_limit(expression) else f"{rendered} LIMIT {ROW_LIMIT}"
    owns_connection = connection is None
    if connection is None:
        context = prepared_read_only_connection(use_approved_snapshot=bool(tables))
        connection = context.__enter__()
    try:
        plan = connection.execute(f"EXPLAIN {guarded_sql}").fetchall()
    except duckdb.Error as exc:
        return ValidationResult(False, checks, f"Schema or dialect verification failed: {exc}.")
    finally:
        if owns_connection:
            context.__exit__(None, None, None)
    checks.extend(["explain_passed", f"preview_limit_{ROW_LIMIT}"])
    return ValidationResult(
        True,
        checks,
        sql=guarded_sql,
        referenced_tables=sorted(tables),
        referenced_columns=sorted(visible_columns),
        explain_summary=f"DuckDB EXPLAIN accepted {len(plan)} plan row(s).",
    )


def _projection_aliases(expression: exp.Expression) -> set[str]:
    return {alias.alias for alias in expression.find_all(exp.Alias)}


def _is_join_key(column: exp.Column) -> bool:
    parent = column.parent
    return isinstance(parent, exp.EQ) and isinstance(parent.parent, exp.Join)


def _has_limit(expression: exp.Expression) -> bool:
    return expression.args.get("limit") is not None


def validate(sql: str, connection: duckdb.DuckDBPyConnection) -> ValidationResult:
    """Compatibility entry point used by the deterministic v1 path."""
    return validate_sql(sql, connection, schema=DEMO_SCHEMA)

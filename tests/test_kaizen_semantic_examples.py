from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_error_budget_example_reports_percentage_and_errors_above_boundary():
    text = (ROOT / "skills/backend-databases/database-reliability/SKILL.md").read_text(encoding="utf-8")
    assert "100.0 * SUM(duration_seconds) / 604.8" in text
    assert "mysql_query_duration_seconds_count[5m])) - sum(rate(mysql_query_duration_seconds_bucket" in text


def test_permission_example_respects_tenant_deny_before_admin_bypass():
    text = (ROOT / "skills/saas/multi-tenant-saas-architecture/SKILL.md").read_text(encoding="utf-8")
    deny = text.index("if (userPermissions.denied(userId, tenantId, permission)) return false;")
    admin = text.index("isScopedAdministrativePermission(permission)")
    assert deny < admin
    assert "tenant-scoped actions" in text

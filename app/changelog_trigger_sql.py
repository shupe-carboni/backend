"""
For generating triggers on vendor reference tables where a history is needed.
The assumption is that there is one column to watch, such as a price point or a 
group assignment in a reference table that determines what price is shown or calulated
for a customer user.

"""

Column = tuple[str]  # name, type, constraints


def generate_new_trigger_sql(
    target_table: str,
    target_change_col: Column,
) -> str:
    target_change_col_name, _, _ = target_change_col
    target_change_col_changelog_id_col: Column = (
        f"{target_change_col_name}_id",
        "int",
        f"references {target_table}(id)",
    )
    changlog_table = f"{target_table}_changelog"
    changelog_ids: list[Column] = [
        ("id", "serial", "primary key"),
        target_change_col_changelog_id_col,
    ]
    changelog_date_user_commment: list[Column] = [
        ("effective_date", "timestamp", "default CURRENT_TIMESTAMP"),
        ("user_id", "int", "references sca_users(id)"),
        ("comment", "text", ""),
    ]
    changelog_columns = (
        changelog_ids + [target_change_col] + changelog_date_user_commment
    )
    create_table_col_def = ", ".join(
        [" ".join([e for e in col if e]) for col in changelog_columns]
    )
    insert_col_def = f"{target_change_col_changelog_id_col[0]},{target_change_col_name}"

    target_table_update_fn = f"update_{target_table}_function()"
    target_table_update_trigger = f"update_{target_table}"

    target_table_insert_fn = f"insert_{target_table}_function()"
    target_table_insert_trigger = f"insert_{target_table}"

    sql = f"""
    --create changelog table
    CREATE TABLE {changlog_table} ({create_table_col_def});

    -- create function for the update trigger
    CREATE OR REPLACE FUNCTION {target_table_update_fn}
    RETURNS TRIGGER AS $$
    BEGIN
        IF OLD.{target_change_col_name} != NEW.{target_change_col_name} THEN
            INSERT INTO {changlog_table} ({insert_col_def})
            VALUES (OLD.id, NEW.{target_change_col_name});
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    -- create trigger for update
    CREATE TRIGGER {target_table_update_trigger}
    BEFORE UPDATE ON {target_table}
    FOR EACH ROW
    EXECUTE FUNCTION {target_table_update_fn};

    -- create function for insert trigger
    CREATE OR REPLACE FUNCTION {target_table_insert_fn}
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO {changlog_table} ({insert_col_def})
        VALUES (NEW.id, NEW.{target_change_col_name});
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    -- create trigger for insert
    CREATE TRIGGER {target_table_insert_trigger}
    AFTER INSERT ON {target_table}
    FOR EACH ROW
    EXECUTE FUNCTION {target_table_insert_fn};
    """
    return sql

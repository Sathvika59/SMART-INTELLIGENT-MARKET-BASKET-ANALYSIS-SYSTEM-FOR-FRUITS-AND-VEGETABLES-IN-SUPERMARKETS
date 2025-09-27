import pymysql

def save_to_mysql(itemsets_df, rules_df, searched_item=None,
                  host="localhost", user="root", password="sathvika@123", database="mba_db"):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO association_rules
        (searched_item, antecedents, consequents, support, confidence, lift, explanation)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        inserted_count = 0

        for _, row in rules_df.iterrows():
            antecedents = row["antecedents"]
            if isinstance(antecedents, (set, frozenset)):
                antecedents = ", ".join(sorted(list(antecedents)))
            else:
                antecedents = str(antecedents)

            consequents = row["consequents"]
            if isinstance(consequents, (set, frozenset)):
                consequents = ", ".join(sorted(list(consequents)))
            else:
                consequents = str(consequents)

            cursor.execute(insert_query, (
                searched_item if searched_item else "",
                antecedents,
                consequents,
                float(row["support"]),
                float(row["confidence"]),
                float(row["lift"]),
                row.get("Explanation", "")
            ))
            inserted_count += 1

        conn.commit()
        cursor.close()
        conn.close()
        return True, f"{inserted_count} rules saved successfully for '{searched_item if searched_item else 'all items'}'."

    except Exception as e:
        return False, str(e)

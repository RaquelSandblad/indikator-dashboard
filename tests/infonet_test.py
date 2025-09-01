from data.infonet_loader import load_pptx_tables

if __name__ == "__main__":
    path = "F\u00f6rsta uppf\u00f6ljning av \u00d6P-steg 2.pptx"
    try:
        tables, text = load_pptx_tables(path)
        print(f"Found {len(tables)} tables")
        for i, t in enumerate(tables):
            print(f"Table {i} columns: {list(t.columns)} | rows: {len(t)}")
        print("Text preview:\n", text[:800])
    except Exception as e:
        print("Error:", e)

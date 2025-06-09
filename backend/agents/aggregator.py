import os
from csv_analyzer import generate_scores_excel

class AggregatorAgent:
    def __init__(self, results_excel):
        self.results_excel = results_excel
        self.error_log = results_excel.replace(".xlsx", "_errors.csv")

    def append_results(self, results):
        # Use real generate_scores_excel to create a professional Excel file
        try:
            # If results.xlsx exists, read existing scores and append
            all_scores = []
            if os.path.exists(self.results_excel):
                # For simplicity, just read the file as a DataFrame and convert to dicts
                import pandas as pd
                df_existing = pd.read_excel(self.results_excel)
                all_scores = df_existing.to_dict(orient="records")
            all_scores.extend(results)
            excel_bytes = generate_scores_excel(all_scores)
            with open(self.results_excel, "wb") as f:
                f.write(excel_bytes.read())
        except Exception as e:
            print(f"Error writing results Excel: {e}")

        # Log errors to CSV
        error_rows = []
        for res in results:
            if not res.get("repo_access", True) or res.get("grade", 0) == 0:
                error_rows.append({
                    "Name": res.get("name", ""),
                    "GitHub URL": res.get("repo_url", ""),
                    "Error": "; ".join(res.get("feedback", []))
                })
        if error_rows:
            import pandas as pd
            err_df = pd.DataFrame(error_rows)
            if not os.path.exists(self.error_log):
                err_df.to_csv(self.error_log, index=False)
            else:
                err_df.to_csv(self.error_log, mode="a", header=False, index=False)

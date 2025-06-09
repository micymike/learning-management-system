import threading
import queue
import time

from analyzer import AnalyzerAgent

class ControllerAgent:
    def __init__(self, students, rubric, batch_size, analyzer_slots, aggregator, timeout=120):
        self.students = students
        self.rubric = rubric
        self.batch_size = batch_size
        self.analyzer_slots = analyzer_slots
        self.aggregator = aggregator
        self.timeout = timeout

    def run_batches(self):
        total = len(self.students)
        batches = [self.students[i:i+self.batch_size] for i in range(0, total, self.batch_size)]
        print(f"Total students: {total}, Batches: {len(batches)}")

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n=== Processing Batch {batch_num}/{len(batches)} ===")
            results = self._process_batch(batch)
            self.aggregator.append_results(results)
            print(f"Batch {batch_num} complete. Results appended.")

    def _process_batch(self, batch):
        result_queue = queue.Queue()
        threads = []
        for student in batch:
            t = threading.Thread(
                target=self._run_analyzer,
                args=(student, self.rubric, result_queue)
            )
            threads.append(t)
            t.start()
            if len(threads) >= self.analyzer_slots:
                for th in threads:
                    th.join(timeout=self.timeout)
                threads = []

        # Join any remaining threads
        for th in threads:
            th.join(timeout=self.timeout)

        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        # If any analyzer did not return, add a placeholder
        if len(results) < len(batch):
            missing = len(batch) - len(results)
            for i in range(missing):
                student = batch[len(results) + i]
                results.append({
                    "name": student["Name"],
                    "grade": 0,
                    "feedback": ["Analyzer timed out or failed."],
                    "repo_access": False
                })
        return results

    def _run_analyzer(self, student, rubric, result_queue):
        try:
            analyzer = AnalyzerAgent(student, rubric)
            result = analyzer.analyze()
            result_queue.put(result)
        except Exception as e:
            result_queue.put({
                "name": student["Name"],
                "grade": 0,
                "feedback": [f"Analyzer error: {str(e)}"],
                "repo_access": False
            })

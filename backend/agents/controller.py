import threading
import queue
import time

from agents.analyzer import AnalyzerAgent

class ControllerAgent:
    def __init__(self, students, rubric, batch_size, analyzer_slots, aggregator, timeout=120):
        self.students = students
        self.rubric = rubric
        self.batch_size = batch_size
        self.analyzer_slots = analyzer_slots
        self.aggregator = aggregator
        self.timeout = timeout

    def run_batches(self):
        total_students = len(self.students)
        print(f"[Controller] Total students: {total_students}")
        batches = [
            self.students[i:i + self.batch_size]
            for i in range(0, total_students, self.batch_size)
        ]
        print(f"[Controller] Total batches: {len(batches)} (batch size: {self.batch_size})")

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n[Controller] Processing batch {batch_num}/{len(batches)} (size: {len(batch)})")
            results = self._run_analyzers(batch)
            self.aggregator.append_results(results)
            print(f"[Controller] Batch {batch_num} complete. Results aggregated.")

    def _run_analyzers(self, batch):
        results = []
        q = queue.Queue()
        threads = []
        lock = threading.Lock()

        def worker(student):
            try:
                analyzer = AnalyzerAgent(student, self.rubric)
                result = analyzer.analyze()
                with lock:
                    results.append(result)
            except Exception as e:
                with lock:
                    results.append({
                        "name": student.get("Name") or student.get("name"),
                        "grade": 0,
                        "feedback": [f"Error: {str(e)}"],
                        "rubric_breakdown": {},
                        "repo_access": False
                    })

        for student in batch:
            q.put(student)

        def thread_target():
            while True:
                try:
                    student = q.get_nowait()
                except queue.Empty:
                    break
                worker(student)
                q.task_done()

        for _ in range(min(self.analyzer_slots, len(batch))):
            t = threading.Thread(target=thread_target)
            t.start()
            threads.append(t)

        # Wait for all threads to finish or timeout
        start_time = time.time()
        for t in threads:
            t.join(timeout=self.timeout)
        elapsed = time.time() - start_time
        print(f"[Controller] Batch processed in {elapsed:.2f} seconds")
        return results

import React from 'react';

const RubricTemplate = () => {
  const rubricContent = `Main Criterion: Correctness of Code [12 points]
- Level (0-0): Incorrect Code - The code provided by the student is fundamentally incorrect, and it does not fulfill the specified requirements.
- Level (1-3): The code contains some correct elements but also includes significant errors that impact its functionality.
- Level (4-8): The majority of the code is correct, with only minor errors that do not significantly affect its overall functionality.
- Level (10-12): The code is entirely correct, meeting all specified requirements and functioning as intended.

Code Structure [8 points]
- Level (0-2): Poor structure with no clear organization
- Level (3-5): Basic structure with some organization
- Level (6-8): Well-structured code with clear organization

Documentation [8 points]
- Level (0-2): Little to no documentation
- Level (3-5): Basic documentation present
- Level (6-8): Comprehensive documentation

Error Handling [8 points]
- Level (0-2): No error handling
- Level (3-5): Basic error handling
- Level (6-8): Comprehensive error handling

Testing [8 points]
- Level (0-2): No testing
- Level (3-5): Basic testing
- Level (6-8): Comprehensive testing`;

  const downloadRubric = () => {
    const blob = new Blob([rubricContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'working_rubric.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Working Rubric Template</h2>
      <p className="mb-4">
        This is a rubric template that works with the backend. You can download it and use it as a starting point.
      </p>
      <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-auto max-h-96 mb-4">
        {rubricContent}
      </pre>
      <button
        onClick={downloadRubric}
        className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded"
      >
        Download Rubric Template
      </button>
    </div>
  );
};

export default RubricTemplate;
import React from 'react';

const SampleRubric = ({ onUse }) => {
  const sampleRubric = `Main Criterion: Correctness of Code [12 points]
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

  return (
    <div className="bg-blue-50 p-4 rounded-md border border-blue-200 mt-4">
      <h3 className="text-sm font-medium text-blue-800 mb-2">Proper Rubric Format</h3>
      <pre className="text-xs text-blue-700 bg-blue-100 p-2 rounded overflow-x-auto mb-2 max-h-60 overflow-y-auto">
        {sampleRubric}
      </pre>
      <button
        type="button"
        onClick={() => onUse && onUse(sampleRubric)}
        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
      >
        Use this sample
      </button>
    </div>
  );
};

export default SampleRubric;
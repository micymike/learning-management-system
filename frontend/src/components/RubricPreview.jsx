import React from 'react';

const RubricPreview = ({ rubricText }) => {
  const parseRubricText = (text) => {
    const lines = text.split('\n').filter(line => line.trim());
    const criteria = [];
    let currentCriterion = null;

    lines.forEach(line => {
      // Check if this is a criterion header (contains points)
      if (line.includes('[') && line.includes('points]')) {
        if (currentCriterion) {
          criteria.push(currentCriterion);
        }
        const name = line.split('[')[0].trim();
        const points = line.match(/\[(\d+)\s*points?\]/i)?.[1] || "0";
        currentCriterion = {
          name,
          points: parseInt(points),
          levels: []
        };
      }
      // Check if this is a level description
      else if (line.startsWith('-') && currentCriterion) {
        const levelMatch = line.match(/\((\d+)-(\d+)\):/);
        if (levelMatch) {
          const description = line.split(':')[1]?.trim() || '';
          currentCriterion.levels.push({
            range: `${levelMatch[1]}-${levelMatch[2]}`,
            description
          });
        }
      }
    });

    if (currentCriterion) {
      criteria.push(currentCriterion);
    }

    return criteria;
  };

  const criteria = parseRubricText(rubricText);

  return (
    <div className="mt-4 border rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 border-b">
        <h3 className="text-sm font-medium text-gray-700">Rubric Preview</h3>
      </div>
      <div className="p-4">
        {criteria.map((criterion, index) => (
          <div key={index} className="mb-6 last:mb-0">
            <div className="flex justify-between items-baseline mb-2">
              <h4 className="text-sm font-medium text-gray-900">{criterion.name}</h4>
              <span className="text-xs text-gray-500">{criterion.points} points</span>
            </div>
            <div className="space-y-2">
              {criterion.levels.map((level, levelIndex) => (
                <div key={levelIndex} className="flex items-start">
                  <div className="flex-shrink-0 w-16 text-xs text-gray-500">
                    {level.range}:
                  </div>
                  <div className="flex-grow text-sm text-gray-700">
                    {level.description}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RubricPreview;

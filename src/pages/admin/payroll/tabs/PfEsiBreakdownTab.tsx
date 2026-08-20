import React from 'react';

const PfEsiBreakdownTab = ({ type, cycleId, branchId }: { type: 'pf' | 'esi'; cycleId: string; branchId: string }) => {
  return <div className="p-4">{type.toUpperCase()} Breakdown UI</div>;
};
export default PfEsiBreakdownTab;

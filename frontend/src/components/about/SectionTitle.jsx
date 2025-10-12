import React from "react";

const SectionTitle = ({ title, subtitle }) => {
  return (
    <div className="text-center my-10">
      <h2 className="text-3xl font-bold text-gray-800 ">{title}</h2>
      {subtitle && (
        <p className="mt-2 text-gray-600">{subtitle}</p>
      )}
    </div>
  );
};

export default SectionTitle;

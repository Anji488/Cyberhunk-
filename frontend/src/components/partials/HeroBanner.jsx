import React from "react";

export default function HeroBanner({ title, subtitle, image}) {
  return (
    <section
      className="relative w-full h-[92vh] flex items-center justify-center text-center"
      style={{
        backgroundImage: `url(${image})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >

      <div className="relative z-10 text-white px-6 max-w-4xl">
        <h1 className="text-5xl font-extrabold mb-4 drop-shadow-lg">{title}</h1>
        <p className="text-lg md:text-xl leading-relaxed drop-shadow-md">{subtitle}</p>
      </div>
    </section>
  );
}

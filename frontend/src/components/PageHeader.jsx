export default function PageHeader({ icon, title, subtitle }) {
  return (
    <section className="hero-gradient text-white">
      <div className="leaf-pattern absolute inset-0 opacity-20" />
      <div className="relative mx-auto max-w-7xl px-4 py-14 text-center">
        {icon && <div className="mb-3 text-5xl">{icon}</div>}
        <h1 className="text-3xl font-extrabold sm:text-4xl">{title}</h1>
        {subtitle && <p className="mx-auto mt-2 max-w-2xl text-herb-100">{subtitle}</p>}
      </div>
    </section>
  );
}

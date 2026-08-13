import "./index.css";
import useFetchProjects from "./hooks/api";
import { useMemo } from "react";
import type { CryptoProject } from "./types";

export default function App() {
  const {
    projects,
    search,
    fdvMax,
    sortBy,
    sortOrder,
    loading,
    error,
    setSearch,
    setFdvMax,
    setSortBy,
    setSortOrder,
  } = useFetchProjects();

  const filteredProjects = useMemo(() => {
    const query = search.trim().toLowerCase();
    const maxFdv = Number(fdvMax);

    return projects.filter((project: CryptoProject) => {
      const matchesSearch =
        !query || project.name.toLowerCase().includes(query);

      const matchesFdv =
        !fdvMax ||
        (Number.isFinite(maxFdv) && project.fully_diluted_valuation < maxFdv);

      return matchesSearch && matchesFdv;
    });
  }, [projects, search, fdvMax]);
  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

  return (
    <main className="page">
      <header>
        <p className="eyebrow">COINGECKO SCREENER</p>
        <h1>Crypto Projects</h1>
        <p className="subtitle">
          Projects matching the required market, supply, listing, FDV and TVL
          criteria.
        </p>
      </header>

      <section className="controls" aria-label="Filters and sorting">
        <label>
          Search by name
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="e.g. zora"
          />
        </label>

        <label>
          Max FDV ($)
          <input
            type="number"
            min="1"
            value={fdvMax}
            onChange={(e) => setFdvMax(e.target.value)}
            placeholder="100000000"
          />
        </label>

        <label>
          Sort by
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          >
            <option value="market_cap">Market Capitalization</option>
            <option value="volume_24h">24h Trading Volume</option>
          </select>
        </label>

        <label>
          Order
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as typeof sortOrder)}
          >
            <option value="desc">Highest first</option>
            <option value="asc">Lowest first</option>
          </select>
        </label>
      </section>

      {loading && <p className="state">Loading projects from backend…</p>}
      {error && <p className="state error">Could not load projects: {error}</p>}

      {!loading && !error && (
        <>
          <div className="result-meta">
            Showing {filteredProjects.length} project
            {filteredProjects.length === 1 ? "" : "s"}
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Market Cap</th>
                  <th>24h Volume</th>
                  <th>FDV</th>
                  <th>TVL</th>
                  <th>Supply</th>
                </tr>
              </thead>
              <tbody>
                {filteredProjects.map((project) => (
                  <tr key={project.id}>
                    <td>
                      <div className="project">
                        {project.image ? (
                          <img src={project.image} alt="" />
                        ) : (
                          <div className="avatar" />
                        )}
                        <div>
                          <strong>{project.name}</strong>
                          <span>{project.symbol}</span>
                        </div>
                      </div>
                    </td>
                    <td>{money.format(project.market_cap)}</td>
                    <td>{money.format(project.total_volume)}</td>
                    <td>{money.format(project.fully_diluted_valuation)}</td>
                    <td>{money.format(project.total_value_locked)}</td>
                    <td>{project.max_supply.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredProjects.length === 0 && (
              <p className="state">No projects match the current filters.</p>
            )}
          </div>
        </>
      )}
    </main>
  );
}

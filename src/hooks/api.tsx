import { useEffect, useState } from "react";
import type { CryptoProject, ApiResponse } from "../types";

export default function fetchProjects() {
  const [projects, setProjects] = useState<CryptoProject[]>([]);
  const [search, setSearch] = useState("");
  const [fdvMax, setFdvMax] = useState("100000000");

  const [sortBy, setSortBy] = useState<"market_cap" | "volume_24h">(
    "market_cap",
  );

  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

  useEffect(() => {
    const controller = new AbortController();

    async function loadProjects() {
      setLoading(true);
      setError("");

      try {
        const params = new URLSearchParams({
          sort_by: sortBy,
          order: sortOrder,
        });

        const response = await fetch(`${API_BASE}/api/crypto?${params}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`);
        }

        const data: ApiResponse = await response.json();

        setProjects(data.items);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }

        setError(
          err instanceof Error ? err.message : "Failed to load projects",
        );
      } finally {
        setLoading(false);
      }
    }

    loadProjects();

    return () => controller.abort();
  }, [sortBy, sortOrder]);

  return {
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
  };
}

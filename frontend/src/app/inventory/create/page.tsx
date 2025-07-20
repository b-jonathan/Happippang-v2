"use client";

import { api } from "@/lib/api";
import { Inventory, InventoryBulk } from "@/types/inventory";
import { Item } from "@/types/item";
import { Store } from "@/types/store";
import { useRouter } from "next/navigation";
import React, { useEffect, useState, FormEvent } from "react";

/**
 * Dynamic version ↔ FastAPI
 * --------------------------------------------------------------
 * • GET /stores  → fills shop dropdown
 * • GET /items   → fills item rows
 * • POST /inventory (payload logged for now)
 * --------------------------------------------------------------
 * Environment: set NEXT_PUBLIC_API_URL=http://localhost:8000
 */

// ----------------------- Types ------------------------------------ //

interface RowState {
  db: number;
  pg: number;
}

// --------------------- Component ---------------------------------- //
export default function CreateInventory() {
  const router = useRouter();
  const [stores, setStores] = useState<Store[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [shopId, setShopId] = useState<string>("");
  const [date, setDate] = useState<string>("");

  // set today’s date on first client render
  useEffect(() => {
    setDate(new Date().toISOString().split("T")[0]);
  }, []);
  const [rows, setRows] = useState<Record<string, RowState>>({});

  // ————— Fetch stores & items on mount ————— //
  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        const [storesRes, itemsRes] = await Promise.all([
          api.get<Store[]>(`/stores/`),
          api.get<Item[]>(`/items/`),
        ]);

        if (cancelled) return; // 🔹 bail if component unmounted

        // Axios gives parsed JSON right away
        const storesData = storesRes.data;
        const itemsData = itemsRes.data;

        console.log(storesData);
        setStores(storesData);
        setItems(itemsData);
        setShopId(storesData[0]?.id ?? "");
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ?? err?.message ?? "Unknown error"
        );
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  // ————— Handlers ————— //
  const handleInput = (id: string, field: keyof RowState, val: string) => {
    const num = parseInt(val, 10);
    setRows(prev => ({
      ...prev,
      [id]: { ...prev[id], [field]: isNaN(num) ? 0 : num },
    }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const payload: InventoryBulk = {
      store_id: shopId,
      date,
      items: items.map(item => ({
        item_id: item.id,
        db: rows[item.id]?.db ?? 0,
        pg: rows[item.id]?.pg ?? 0,
      })),
    };

    try {
      setLoading(true);
      const res = await api.post<Inventory[]>("/inventory/bulk", payload);
      console.log("Inserted:", res.data);
      router.push("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? err.message);
    } finally {
      setLoading(false);
    }
  };

  // ————— UI ————— //
  if (loading) return <p className="p-4">Loading…</p>;
  if (error) return <p className="p-4 text-red-600">Error: {error}</p>;

  return (
    <div className="mx-auto max-w-4xl p-4">
      <h1 className="mb-4 text-2xl font-bold">Happippang Daily Input</h1>

      {/* Controls */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row">
        <label className="flex items-center gap-2">
          <span className="font-medium">Shop:</span>
          <select
            className="rounded border bg-white p-2"
            value={shopId}
            onChange={e => setShopId(e.target.value)}
          >
            {stores.map(s => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-2">
          <span className="font-medium">Date:</span>
          <input
            type="date"
            className="rounded border bg-white p-2"
            value={date}
            onChange={e => setDate(e.target.value)}
          />
        </label>
      </div>

      {/* Table */}
      <form onSubmit={handleSubmit}>
        <div className="overflow-x-auto rounded-lg border dark:border-gray-700">
          <div className="scrollbar-thin scrollbar-track-transparent scrollbar-thumb-transparent hover:scrollbar-thumb-gray-400/40 dark:hover:scrollbar-thumb-gray-500/50 max-h-[70vh] overflow-y-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-700">
              <thead className="bg-gray-50 text-white dark:bg-gray-800">
                <tr className="sticky top-0 z-20 bg-inherit">
                  <th className="px-4 py-3 text-left font-semibold tracking-wide">
                    Item
                  </th>
                  <th className="px-4 py-3 text-right font-semibold tracking-wide">
                    DB
                  </th>
                  <th className="px-4 py-3 text-right font-semibold tracking-wide">
                    PG
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {items.map(item => (
                  <tr key={item.id}>
                    <td className="px-4 py-2 leading-tight font-medium">
                      {`${item.category} ${item.name}`}
                    </td>
                    <td className="px-4 py-2 text-right">
                      <input
                        type="number"
                        min={0}
                        value={rows[item.id]?.db ?? ""}
                        onChange={e =>
                          handleInput(item.id, "db", e.target.value)
                        }
                        className="w-20 rounded-md border bg-white p-1 text-right"
                        placeholder="0"
                      />
                    </td>
                    <td className="px-4 py-2 text-right">
                      <input
                        type="number"
                        min={0}
                        value={rows[item.id]?.pg ?? ""}
                        onChange={e =>
                          handleInput(item.id, "pg", e.target.value)
                        }
                        className="w-20 rounded-md border bg-white p-1 text-right"
                        placeholder="0"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <button
          type="submit"
          className="mt-6 rounded-md bg-black px-6 py-2 font-medium text-white shadow hover:opacity-90"
        >
          Save
        </button>
      </form>
    </div>
  );
}

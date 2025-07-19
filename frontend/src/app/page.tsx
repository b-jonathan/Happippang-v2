"use client";

import React, { useState, FormEvent } from "react";

/**
 * Table‑style form with two numeric inputs per item (in / out).
 * Columns: Item | In | Out
 */

// ------------ Static data ------------------------------------------- //

const SHOPS = [
  { id: "carrefour-cbd-pluit", name: "Carrefour CBD Pluit" },
  { id: "central-park", name: "Central Park" },
  { id: "kota-kasablanka", name: "Kota Kasablanka" },
] as const;

const RAW_ITEMS = [
  { name: "ORI", category: "Bluder", cost: 5000 },
  { name: "Choco", category: "Bluder", cost: 7000 },
  { name: "Cheese", category: "Bluder", cost: 7000 },
  { name: "ChocoCheese", category: "Bluder", cost: 7000 },
  { name: "Smoked Beef", category: "Bluder", cost: 7000 },
  { name: "Abon", category: "Bluder", cost: 7000 },
  { name: "Bluberry", category: "Bluder", cost: 7000 },
  { name: "Bunny", category: "SC", cost: 3000 },
  { name: "Bear", category: "SC", cost: 3000 },
  { name: "Cat", category: "SC", cost: 3000 },
  { name: "Cok", category: "Wassant", cost: 17500 },
  { name: "Keju", category: "Wassant", cost: 17500 },
  { name: "Mix", category: "Wassant", cost: 17500 },
  { name: "Kotak", category: "Milky", cost: 18000 },
  { name: "Bunny", category: "Milky", cost: 12000 },
  { name: "Cat.Duo", category: "Milky", cost: 12000 },
  { name: "Bear", category: "Milky", cost: 12000 },
  { name: "meses", category: "LJ", cost: 5250 },
  { name: "cheese", category: "LJ", cost: 6000 },
  { name: "rainbow", category: "LJ", cost: 5500 },
  { name: "duo", category: "LJ", cost: 6500 },
  { name: "Manis Kotak", category: "Bagelen", cost: 10000 },
  { name: "Manis Cat", category: "Bagelen", cost: 3000 },
  { name: "Manis Bunny", category: "Bagelen", cost: 3000 },
  { name: "Manis Bear", category: "Bagelen", cost: 3000 },
  { name: "Garlic Kotak", category: "Bagelen", cost: 10000 },
  { name: "Garlic Cat", category: "Bagelen", cost: 3000 },
  { name: "Garlic Bunny", category: "Bagelen", cost: 3000 },
  { name: "Garlic Bear", category: "Bagelen", cost: 3000 },
  { name: "Cok", category: "RJ", cost: 5000 },
  { name: "Cokju", category: "RJ", cost: 5000 },
  { name: "Piscok", category: "RJ", cost: 6000 },
  { name: "Abon", category: "RJ", cost: 6000 },
  { name: "Sosis", category: "RJ", cost: 6000 },
  { name: "Spicy", category: "RJ", cost: 8000 },
  { name: "Baso", category: "RJ", cost: 6000 },
  { name: "Cheese Bomb", category: "RJ", cost: 8000 },
  { name: "Butter Roll", category: "GL", cost: 14000 },
  { name: "Roti Sisir Mocha", category: "GL", cost: 8000 },
  { name: "Roti Sisir Cheese", category: "GL", cost: 8000 },
] as const;

const ITEMS = RAW_ITEMS.map(it => ({
  ...it,
  id: `${it.name.toLowerCase().replace(/\\s+/g, "-")}-${it.category.toLowerCase()}`,
}));

// ------------ Component -------------------------------------------- //

interface RowState {
  db: number;
  pg: number;
}

export default function ShopItemGridForm() {
  const [shopId, setShopId] = useState<string>(SHOPS[0].id);
  const [date, setDate] = useState<string>(() => {
    const today = new Date();
    return today.toISOString().split("T")[0]; // YYYY-MM-DD
  });
  const [rows, setRows] = useState<Record<string, RowState>>({});

  const handleInput = (id: string, field: keyof RowState, val: string) => {
    const num = parseInt(val, 10);
    setRows(prev => ({
      ...prev,
      [id]: { ...prev[id], [field]: isNaN(num) ? 0 : num },
    }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      shopId,
      date,
      items: ITEMS.map(it => ({
        id: it.id,
        inQty: rows[it.id]?.db ?? 0,
        outQty: rows[it.id]?.pg ?? 0,
      })),
    };
    console.log("🚀 Submitting", payload);
  };

  return (
    <div className="mx-auto max-w-4xl p-4">
      <h1 className="mb-4 text-2xl font-bold">Happippang Daily Input</h1>

      <label className="mb-6 block flex items-center gap-4">
        <span className="mr-2 font-medium">Shop:</span>
        <select
          className="0 rounded border bg-white p-2"
          value={shopId}
          onChange={e => setShopId(e.target.value)}
        >
          {SHOPS.map(s => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>

        <span className="font-medium">Date:</span>
        <input
          type="date"
          className="rounded border bg-white p-2"
          value={date}
          onChange={e => setDate(e.target.value)}
        />
      </label>

      <label className="mb-6 flex items-center gap-2"></label>

      <form onSubmit={handleSubmit}>
        <div className="overflow-x-auto rounded-lg border dark:border-gray-700">
          <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-700">
            <thead className="bg-gray-50 text-white dark:bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left font-semibold tracking-wide">
                  Item
                </th>
                <th className="px-4 py-3 text-right font-semibold tracking-wide">
                  DB
                </th>
                <th className="px-4 py-3 text-right font-semibold tracking-wide">
                  Penjualan
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {ITEMS.map(item => (
                <tr key={item.id}>
                  <td className="px-4 py-2 leading-tight font-medium">
                    {`${item.category} ${item.name}`}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <input
                      type="number"
                      min={0}
                      value={rows[item.id]?.db ?? ""}
                      onChange={e => handleInput(item.id, "db", e.target.value)}
                      className="w-20 rounded-md border bg-white p-1 text-right"
                      placeholder="0"
                    />
                  </td>
                  <td className="px-4 py-2 text-right">
                    <input
                      type="number"
                      min={0}
                      value={rows[item.id]?.pg ?? ""}
                      onChange={e => handleInput(item.id, "pg", e.target.value)}
                      className="w-20 rounded-md border bg-white p-1 text-right"
                      placeholder="0"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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

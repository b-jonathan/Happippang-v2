export interface InventoryLine {
  item_id: string;
  db: number;
  pg: number;
}

export interface Inventory extends InventoryLine {
  id: string;
  store_id: string;
  date: string;
}

export interface InventoryBulk {
  store_id: string;
  date: string;
  items: InventoryLine[];
}

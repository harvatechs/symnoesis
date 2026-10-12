<script lang="ts">
  import { onMount } from "svelte";
  import { intToGray, grayToInt, pixelIdFromBits, intToBits } from "@symnoesis/core";

  interface PixelData {
    col: number;
    row: number;
    pixelId: string;
    hBits: number[];
    mBits: number[];
    isZ5: boolean;
  }

  let selectedPixel: PixelData | null = null;
  const gridCells: PixelData[] = [];

  for (let r = 0; r < 16; r++) {
    const mCode = intToGray(r);
    const mBits = intToBits(mCode, 4);
    for (let c = 0; c < 16; c++) {
      const hCode = intToGray(c);
      const hBits = intToBits(hCode, 4);
      const pid = pixelIdFromBits(hBits, mBits);
      const isZ5 = (hBits[0] === 0 || hBits[3] === 0) && mBits[1] === 0;
      gridCells.push({
        col: c,
        row: r,
        pixelId: pid,
        hBits,
        mBits,
        isZ5,
      });
    }
  }

  function selectCell(cell: PixelData) {
    selectedPixel = cell;
  }
</script>

<div class="map-container">
  <div class="grid-wrapper">
    <div class="grid-16x16" role="grid" aria-label="Symnoesis 16 by 16 Gray-coded Grid Map">
      {#each gridCells as cell}
        <button
          type="button"
          class="grid-cell"
          class:z5={cell.isZ5}
          class:active={selectedPixel && selectedPixel.pixelId === cell.pixelId}
          on:click={() => selectCell(cell)}
          aria-label={"Pixel " + cell.pixelId + ", row " + cell.row + ", col " + cell.col}
        >
        </button>
      {/each}
    </div>
  </div>

  <div class="details-panel" aria-live="polite">
    <h3>Inspector</h3>
    {#if selectedPixel}
      <p><strong>Pixel ID:</strong> {selectedPixel.pixelId}</p>
      <p><strong>Grid Coordinates:</strong> Col {selectedPixel.col}, Row {selectedPixel.row}</p>
      <p><strong>Human Code (H1-H4):</strong> {selectedPixel.hBits.join("")}</p>
      <p><strong>Machine Code (M1-M4):</strong> {selectedPixel.mBits.join("")}</p>
      <p><strong>Z5 Dependence Condition:</strong> {selectedPixel.isZ5 ? "True" : "False"}</p>
    {:else}
      <p class="muted">Select any cell on the 16×16 grid to view its Gray coordinates and bits.</p>
    {/if}
  </div>
</div>

<style>
  .map-container {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
    margin: 1.5rem 0;
    flex-wrap: wrap;
  }
  .grid-wrapper {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 0.75rem;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  }
  .grid-16x16 {
    display: grid;
    grid-template-columns: repeat(16, 22px);
    grid-template-rows: repeat(16, 22px);
    gap: 2px;
    background: #f3f4f6;
    padding: 3px;
    border-radius: 4px;
  }
  .grid-cell {
    width: 22px;
    height: 22px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    cursor: pointer;
    padding: 0;
    transition: background-color 0.1s ease, border-color 0.1s ease;
  }
  .grid-cell:hover, .grid-cell:focus {
    background: #bfdbfe;
    outline: 2px solid #1d4ed8;
  }
  .grid-cell.z5 {
    background: #fef08a;
    border-color: #fde047;
  }
  .grid-cell.active {
    background: #1d4ed8;
    border-color: #1e40af;
  }
  .details-panel {
    flex: 1;
    min-width: 280px;
    padding: 1.5rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    font-family: -apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif;
  }
  .details-panel h3 {
    margin: 0 0 1rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
  }
  .details-panel p {
    margin: 0 0 0.65rem 0;
    font-size: 0.9375rem;
    color: #374151;
    line-height: 1.5;
  }
  .muted {
    color: #6b7280;
  }
</style>

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
    margin: 2rem 0;
  }
  .grid-16x16 {
    display: grid;
    grid-template-columns: repeat(16, 24px);
    grid-template-rows: repeat(16, 24px);
    gap: 2px;
    background: #e2e8f0;
    padding: 4px;
    border-radius: 4px;
  }
  .grid-cell {
    width: 24px;
    height: 24px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    cursor: pointer;
    padding: 0;
  }
  .grid-cell:hover, .grid-cell:focus {
    background: #93c5fd;
    outline: 2px solid #2563eb;
  }
  .grid-cell.z5 {
    background: #fef08a;
  }
  .grid-cell.active {
    background: #3b82f6;
    border-color: #1d4ed8;
  }
  .details-panel {
    min-width: 280px;
    padding: 1.5rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-family: system-ui, sans-serif;
  }
  .muted {
    color: #64748b;
  }
</style>

// banner.js
// Imprime la araña ASCII + un menú/caja centrados y armonizados,
// con colores ANSI.

const fs = require("fs");
const path = require("path");

const RESET = "\x1b[0m";
const DIM = "\x1b[2m";
const CYAN = "\x1b[36m";
const BOLD_CYAN = "\x1b[1;36m";
const MAGENTA = "\x1b[35m";
const WHITE = "\x1b[97m";
const GRAY = "\x1b[90m";

const stripAnsi = (s) => s.replace(/\x1b\[[0-9;]*m/g, "");
const visibleLength = (s) => stripAnsi(s).length;

function colorize(char) {
  if ("@%#".includes(char)) return CYAN + char + RESET;
  if ("MW8B".includes(char)) return CYAN + char + RESET;
  if ("&$*+".includes(char)) return DIM + CYAN + char + RESET;
  if ("=-:.,".includes(char)) return GRAY + char + RESET;
  return char;
}

function printSpider() {
  const art = fs
    .readFileSync(path.join(__dirname, "spider.txt"), "utf8")
    .split("\n")
    .filter((l, i, arr) => !(i === arr.length - 1 && l === ""));

  let artWidth = 0;
  for (const line of art) {
    artWidth = Math.max(artWidth, line.length);
    let colored = "";
    for (const ch of line) colored += colorize(ch);
    console.log(colored);
  }
  return artWidth;
}

function centerLine(text, width) {
  const vis = visibleLength(text);
  const pad = Math.max(0, Math.floor((width - vis) / 2));
  return " ".repeat(pad) + text;
}

function buildBox(lines) {
  const innerWidth = Math.max(...lines.map((l) => visibleLength(l))) + 4;
  const top = MAGENTA + "┌" + "─".repeat(innerWidth - 2) + "┐" + RESET;
  const bottom = MAGENTA + "└" + "─".repeat(innerWidth - 2) + "┘" + RESET;

  const rows = [top];
  for (const line of lines) {
    const vis = visibleLength(line);
    const padTotal = innerWidth - 2 - vis;
    const padLeft = Math.floor(padTotal / 2);
    const padRight = padTotal - padLeft;
    rows.push(
      MAGENTA + "│" + RESET +
      " ".repeat(padLeft) + line + " ".repeat(padRight) +
      MAGENTA + "│" + RESET
    );
  }
  rows.push(bottom);
  return rows;
}

function printMenuBox(lines, width) {
  console.log();
  for (const row of buildBox(lines)) {
    console.log(centerLine(row, width));
  }
  console.log();
}

function printFooter(width) {
  const line = GRAY + "─".repeat(Math.min(width, 46)) + RESET;
  console.log(centerLine(line, width));
  console.log();
}

function mostrarBanner() {
  console.clear();
  const artWidth = printSpider();
  printMenuBox(
    [WHITE + BOLD_CYAN + "GOOGLE MAPS CONTACT SCRAPER" + RESET, "Perú · v2"],
    artWidth
  );
  printFooter(artWidth);
}

module.exports = { mostrarBanner };

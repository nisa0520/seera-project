/* Seera data — palettes, products, conversation flow */

const SEASONS = {
  spring: {
    name: "Spring",
    emoji: "🌸",
    tagline: "Warm · Light · Bright",
    desc: "warm, cerah, dan segar",
    colors: ["#F4A77F", "#F2CB6A", "#A8C77E", "#7BC4C9", "#F4D7C0"],
    gradient: "linear-gradient(135deg,#F4A77F,#F2CB6A,#A8C77E)"
  },
  summer: {
    name: "Summer",
    emoji: "🌊",
    tagline: "Cool · Light · Soft",
    desc: "lembut, sejuk, dan elegan",
    colors: ["#A8C0D6", "#7FA4C2", "#D5C7E0", "#9CAFB7", "#F2E8E0"],
    gradient: "linear-gradient(135deg,#A8C0D6,#D5C7E0,#9CAFB7)"
  },
  autumn: {
    name: "Autumn",
    emoji: "🍂",
    tagline: "Warm · Deep · Earthy",
    desc: "warm, deep, dan earthy",
    colors: ["#A85E40", "#C4863F", "#7B6B47", "#8FA668", "#E8C896"],
    gradient: "linear-gradient(135deg,#A85E40,#C4863F,#7B6B47)"
  },
  winter: {
    name: "Winter",
    emoji: "❄️",
    tagline: "Cool · Deep · Clear",
    desc: "cool, kontras, dan tegas",
    colors: ["#1B3A6B", "#7A1B3A", "#E8E8E8", "#1F1B16", "#5C2B7A"],
    gradient: "linear-gradient(135deg,#1B3A6B,#7A1B3A,#1F1B16)"
  }
};

const FITZPATRICK = [
  { num: 1, name: "Very Fair", hex: "#F5DBC4", sub: "Fitzpatrick I" },
  { num: 2, name: "Fair", hex: "#EAC2A0", sub: "Fitzpatrick II" },
  { num: 3, name: "Medium Fair", hex: "#D4A382", sub: "Fitzpatrick III" },
  { num: 4, name: "Moderate Brown", hex: "#A87858", sub: "Fitzpatrick IV" },
  { num: 5, name: "Brown", hex: "#7A4F36", sub: "Fitzpatrick V" },
  { num: 6, name: "Dark Brown", hex: "#4A2E20", sub: "Fitzpatrick VI" }
];

const PRODUCTS = {
  summer: [
    { id: "P12", title: "Kemeja Linen Powder Blue", price: "Rp 249.000", score: 82, swatches: ["#A8C0D6","#E8E8E8"], bg: "linear-gradient(160deg,#A8C0D6 0%,#C5D4E0 60%,#A8C0D6 100%)" },
    { id: "P34", title: "Blouse Lavender Drape", price: "Rp 199.000", score: 78, swatches: ["#D5C7E0"], bg: "linear-gradient(160deg,#D5C7E0,#C0B0D0)" },
    { id: "P55", title: "Cardigan Sage Mist", price: "Rp 329.000", score: 74, swatches: ["#9CAFB7","#F2E8E0"], bg: "linear-gradient(160deg,#9CAFB7,#B8C8CD)" },
    { id: "P67", title: "Dress Midi Cloud", price: "Rp 419.000", score: 71, swatches: ["#F2E8E0","#A8C0D6"], bg: "linear-gradient(160deg,#F2E8E0,#E0D5C8)" },
    { id: "P88", title: "Tee Cotton Periwinkle", price: "Rp 159.000", score: 68, swatches: ["#7FA4C2"], bg: "linear-gradient(160deg,#7FA4C2,#9DBBD2)" },
    { id: "P91", title: "Scarf Sutra Soft Mauve", price: "Rp 189.000", score: 65, swatches: ["#D5C7E0","#F2E8E0"], bg: "linear-gradient(160deg,#E5DCEC,#D5C7E0)" }
  ],
  spring: [
    { id: "P10", title: "Tee Cotton Peach", price: "Rp 169.000", score: 88, swatches: ["#F4A77F"], bg: "linear-gradient(160deg,#F4A77F,#F8C5A0)" },
    { id: "P22", title: "Blouse Sunny Daffodil", price: "Rp 229.000", score: 84, swatches: ["#F2CB6A"], bg: "linear-gradient(160deg,#F2CB6A,#F5DC92)" },
    { id: "P31", title: "Skirt Pleat Olive Light", price: "Rp 279.000", score: 79, swatches: ["#A8C77E"], bg: "linear-gradient(160deg,#A8C77E,#C0D69A)" },
    { id: "P42", title: "Cardigan Coral Bloom", price: "Rp 349.000", score: 76, swatches: ["#F4A77F","#F4D7C0"], bg: "linear-gradient(160deg,#F4D7C0,#F4A77F)" },
    { id: "P58", title: "Dress Linen Aqua Fresh", price: "Rp 389.000", score: 72, swatches: ["#7BC4C9"], bg: "linear-gradient(160deg,#7BC4C9,#9DD2D6)" },
    { id: "P77", title: "Scarf Cream Apricot", price: "Rp 159.000", score: 69, swatches: ["#F4D7C0"], bg: "linear-gradient(160deg,#F8E5D2,#F4D7C0)" }
  ],
  autumn: [
    { id: "A12", title: "Kemeja Rust Linen", price: "Rp 269.000", score: 89, swatches: ["#A85E40"], bg: "linear-gradient(160deg,#A85E40,#C47A5C)" },
    { id: "A23", title: "Sweater Mustard Knit", price: "Rp 359.000", score: 85, swatches: ["#C4863F"], bg: "linear-gradient(160deg,#C4863F,#D9A05F)" },
    { id: "A34", title: "Blazer Olive Deep", price: "Rp 489.000", score: 81, swatches: ["#7B6B47","#8FA668"], bg: "linear-gradient(160deg,#7B6B47,#9C8B5F)" },
    { id: "A45", title: "Skirt Camel Wool", price: "Rp 329.000", score: 77, swatches: ["#E8C896"], bg: "linear-gradient(160deg,#E8C896,#D4B07A)" },
    { id: "A56", title: "Tee Sage Earth", price: "Rp 179.000", score: 73, swatches: ["#8FA668"], bg: "linear-gradient(160deg,#8FA668,#A8BC85)" },
    { id: "A67", title: "Scarf Terracotta", price: "Rp 199.000", score: 70, swatches: ["#A85E40","#E8C896"], bg: "linear-gradient(160deg,#C47A5C,#A85E40)" }
  ],
  winter: [
    { id: "W12", title: "Kemeja Navy Crisp", price: "Rp 289.000", score: 92, swatches: ["#1B3A6B"], bg: "linear-gradient(160deg,#1B3A6B,#3A5A8B)" },
    { id: "W23", title: "Dress Burgundy Silk", price: "Rp 549.000", score: 88, swatches: ["#7A1B3A"], bg: "linear-gradient(160deg,#7A1B3A,#9C3A5A)" },
    { id: "W34", title: "Blazer Charcoal Sharp", price: "Rp 599.000", score: 84, swatches: ["#1F1B16"], bg: "linear-gradient(160deg,#1F1B16,#3A332A)" },
    { id: "W45", title: "Blouse Pure White", price: "Rp 219.000", score: 81, swatches: ["#E8E8E8"], bg: "linear-gradient(160deg,#FFFFFF,#E8E8E8)" },
    { id: "W56", title: "Knit Royal Plum", price: "Rp 379.000", score: 78, swatches: ["#5C2B7A"], bg: "linear-gradient(160deg,#5C2B7A,#7C4B9A)" },
    { id: "W67", title: "Scarf Ice Silver", price: "Rp 229.000", score: 74, swatches: ["#E8E8E8","#1B3A6B"], bg: "linear-gradient(160deg,#E8E8E8,#C5D4E0)" }
  ]
};

window.SEERA_DATA = { SEASONS, FITZPATRICK, PRODUCTS };

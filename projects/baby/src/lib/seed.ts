import type { NameCandidate, NurseryTask, RegistryItem, Voter } from "./types";

// Seed data is a starting skeleton, not a recommendation list: generic gear
// slots you research into, rather than specific products with prices that go
// stale. Everything here is editable and is replaced by your own data the
// moment you touch it.

const t0 = "2026-01-01T00:00:00.000Z";

function item(
  id: string,
  name: string,
  category: RegistryItem["category"],
  priority: RegistryItem["priority"],
  notes?: string,
): RegistryItem {
  return { id, name, category, priority, status: "researching", notes, createdAt: t0 };
}

export const REGISTRY_SEED: RegistryItem[] = [
  item("r-carseat", "Infant car seat", "travel", "must", "Required to leave the hospital. Check expiry date and stroller compatibility."),
  item("r-stroller", "Stroller", "travel", "must", "Decide frame-vs-travel-system before buying the car seat."),
  item("r-bassinet", "Bassinet or side sleeper", "sleep", "must", "Room-sharing is recommended for the first 6 months."),
  item("r-crib", "Crib + firm mattress", "sleep", "must"),
  item("r-monitor", "Baby monitor", "sleep", "nice", "Audio-only vs video vs wearable — pick one, they all overlap."),
  item("r-swaddles", "Swaddles / sleep sacks", "sleep", "must", "Buy a couple of styles before committing to a set."),
  item("r-bottles", "Bottles + slow-flow nipples", "feeding", "must", "Start with a small variety pack; babies have opinions."),
  item("r-pump", "Breast pump", "feeding", "must", "Often covered by insurance — check before buying."),
  item("r-burp", "Burp cloths", "feeding", "must"),
  item("r-highchair", "High chair", "feeding", "maybe", "Not needed until ~6 months."),
  item("r-diapers", "Newborn + size 1 diapers", "diapering", "must", "Do not stockpile newborn size."),
  item("r-wipes", "Wipes", "diapering", "must"),
  item("r-changingpad", "Changing pad + covers", "diapering", "must"),
  item("r-diaperpail", "Diaper pail", "diapering", "nice"),
  item("r-onesies", "Newborn + 0-3m onesies", "clothing", "must", "Zippers over snaps for night changes."),
  item("r-tub", "Baby bathtub", "bath", "nice"),
  item("r-towels", "Hooded towels + washcloths", "bath", "nice"),
  item("r-carrier", "Baby carrier or wrap", "travel", "nice", "Try before you buy if you can — fit is personal."),
  item("r-playmat", "Play mat", "play", "nice"),
  item("r-thermometer", "Thermometer", "health", "must"),
  item("r-nailcare", "Nail clippers / file", "health", "must"),
  item("r-firstaid", "Infant first aid kit", "health", "nice"),
  item("r-nursingpillow", "Nursing pillow", "postpartum", "nice"),
  item("r-postpartum", "Postpartum recovery kit", "postpartum", "must", "For the parent, not the baby. Easy to forget."),
  item("r-glider", "Glider or nursing chair", "nursery", "nice"),
  item("r-blackout", "Blackout curtains", "nursery", "nice"),
];

export const VOTERS: Voter[] = [
  { id: "a", label: "Parent A" },
  { id: "b", label: "Parent B" },
];

function name(
  id: string,
  n: string,
  style: NameCandidate["style"],
  origin: string,
  meaning: string,
): NameCandidate {
  return { id, name: n, style, origin, meaning, list: "longlist", ratings: {}, createdAt: t0 };
}

export const NAMES_SEED: NameCandidate[] = [
  name("n-1", "Nora", "girl", "Irish / Latin", "Honour, light"),
  name("n-2", "Iris", "girl", "Greek", "Rainbow"),
  name("n-3", "Margot", "girl", "French", "Pearl"),
  name("n-4", "Theodore", "boy", "Greek", "Gift of God"),
  name("n-5", "Emmett", "boy", "English", "Universal, whole"),
  name("n-6", "Silas", "boy", "Latin / Greek", "Of the forest"),
  name("n-7", "Rowan", "neutral", "Gaelic", "Little red one; the rowan tree"),
  name("n-8", "Wren", "neutral", "English", "The bird"),
  name("n-9", "Ellis", "neutral", "Welsh", "Benevolent"),
];

function task(
  id: string,
  title: string,
  area: NurseryTask["area"],
  notes?: string,
): NurseryTask {
  return { id, title, area, status: "todo", notes, createdAt: t0 };
}

export const NURSERY_SEED: NurseryTask[] = [
  task("t-1", "Measure the room and sketch a layout", "logistics", "Do this before ordering furniture."),
  task("t-2", "Decide crib placement (away from windows and cords)", "safety"),
  task("t-3", "Order crib + mattress", "furniture", "Lead times can run weeks — order early."),
  task("t-4", "Order dresser / changing surface", "furniture"),
  task("t-5", "Anchor all furniture to the wall", "safety"),
  task("t-6", "Install blackout window coverings", "textiles"),
  task("t-7", "Cordless blinds or cord cleats", "safety"),
  task("t-8", "Set up closet organizers by size", "storage", "Newborn through 12m — you will get gifts in every size."),
  task("t-9", "Wash and put away first round of clothes", "textiles"),
  task("t-10", "Add a floor lamp or dimmable light for night feeds", "decor", "Overhead lighting at 3am is a mistake."),
  task("t-11", "Install the car seat base and get it checked", "safety"),
  task("t-12", "Pack the hospital bag", "logistics"),
];

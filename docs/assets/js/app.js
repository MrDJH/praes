(() => {
  "use strict";

  const catalogUrl = new URL("./catalog.json", document.baseURI);
  const container = document.querySelector("#presentations");
  const searchInput = document.querySelector("#search");
  const categorySelect = document.querySelector("#category");
  const sortSelect = document.querySelector("#sort");
  const resultCount = document.querySelector("#result-count");

  let presentations = [];

  function normalize(value) {
    return String(value ?? "").toLocaleLowerCase("de-DE").trim();
  }

  function populateCategories(items) {
    const categories = [...new Set(items.map(item => item.category).filter(Boolean))]
      .sort((a, b) => a.localeCompare(b, "de-DE"));

    for (const category of categories) {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categorySelect.append(option);
    }
  }

  function createCard(item) {
    const article = document.createElement("article");
    article.className = "presentation-card";

    if (item.thumbnail) {
      const image = document.createElement("img");
      image.className = "card-thumbnail";
      image.loading = "lazy";
      image.alt = "";
      image.src = `./presentations/${encodeURIComponent(item.slug)}/${item.thumbnail
        .split("/").map(encodeURIComponent).join("/")}`;
      image.addEventListener("error", () => image.remove(), { once: true });
      article.append(image);
    } else {
      const placeholder = document.createElement("div");
      placeholder.className = "card-placeholder";
      placeholder.setAttribute("aria-hidden", "true");
      placeholder.textContent = "P";
      article.append(placeholder);
    }

    const body = document.createElement("div");
    body.className = "card-body";

    const category = document.createElement("span");
    category.className = "card-category";
    category.textContent = item.category || "Allgemein";

    const title = document.createElement("h2");
    title.textContent = item.title;

    const description = document.createElement("p");
    description.className = "card-description";
    description.textContent = item.description || "";

    const footer = document.createElement("div");
    footer.className = "card-footer";

    const date = document.createElement("span");
    date.className = "card-date";
    date.textContent = item.date || "";

    const link = document.createElement("a");
    link.className = "open-link";
    link.href = `./presentations/${encodeURIComponent(item.slug)}/`;
    link.textContent = "Präsentation öffnen";
    link.setAttribute("aria-label", `Präsentation ${item.title} öffnen`);

    footer.append(date, link);
    body.append(category, title, description, footer);
    article.append(body);
    return article;
  }

  function render() {
    const query = normalize(searchInput.value);
    const category = categorySelect.value;
    const sort = sortSelect.value;

    const filtered = presentations.filter(item => {
      if (category && item.category !== category) return false;
      const searchable = normalize([
        item.title,
        item.description,
        item.category,
        ...(Array.isArray(item.tags) ? item.tags : [])
      ].join(" "));
      return !query || searchable.includes(query);
    });

    filtered.sort((a, b) => {
      if (sort === "date-desc") return (b.date || "").localeCompare(a.date || "") || a.title.localeCompare(b.title, "de-DE");
      if (sort === "date-asc") return (a.date || "9999-99-99").localeCompare(b.date || "9999-99-99") || a.title.localeCompare(b.title, "de-DE");
      return a.title.localeCompare(b.title, "de-DE");
    });

    container.replaceChildren();
    resultCount.textContent = `${filtered.length} von ${presentations.length} Präsentationen`;

    if (filtered.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = presentations.length
        ? "Keine passenden Präsentationen gefunden."
        : "Noch keine Präsentationen vorhanden.";
      container.append(empty);
      return;
    }

    const fragment = document.createDocumentFragment();
    for (const item of filtered) fragment.append(createCard(item));
    container.append(fragment);
  }

  async function init() {
    try {
      const response = await fetch(catalogUrl, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const catalog = await response.json();
      if (catalog.schemaVersion !== 1 || !Array.isArray(catalog.presentations)) {
        throw new Error("Unbekanntes oder ungültiges Katalogformat.");
      }
      const slugPattern = /^[a-z0-9][a-z0-9_-]{0,62}$/;
      if (!catalog.presentations.every(item =>
        item && typeof item.slug === "string" && slugPattern.test(item.slug) &&
        typeof item.title === "string" && typeof item.description === "string" &&
        typeof item.category === "string"
      )) {
        throw new Error("Der Katalog enthält ungültige Präsentationseinträge.");
      }
      presentations = catalog.presentations;
      populateCategories(presentations);
      render();
    } catch (error) {
      console.error("Katalog konnte nicht geladen werden:", error);
      container.replaceChildren();
      const message = document.createElement("p");
      message.className = "error-state";
      message.textContent = "Die Übersicht konnte nicht geladen werden. Starte die Bibliothek über tools/serve.py und prüfe catalog.json.";
      container.append(message);
      resultCount.textContent = "Katalog nicht verfügbar";
    }
  }

  searchInput.addEventListener("input", render);
  categorySelect.addEventListener("change", render);
  sortSelect.addEventListener("change", render);
  init();
})();

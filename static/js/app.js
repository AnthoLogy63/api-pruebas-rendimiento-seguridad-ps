const API = "";

async function api(method, path, body) {
  const opts = {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(API + path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Error en la solicitud");
  return data;
}

function toast(msg, type = "success") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = `toast show ${type}`;
  setTimeout(() => el.classList.remove("show"), 3500);
}

function formatDate(str) {
  if (!str) return "—";
  return new Date(str.replace(" ", "T")).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function isVencido(p) {
  if (p.estado !== "activo") return false;
  return new Date(p.fecha_devolucion_esperada.replace(" ", "T")) < new Date();
}

// Navigation
document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".section").forEach((s) => s.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.section).classList.add("active");
  });
});

// Modals
document.querySelectorAll(".modal-close").forEach((btn) => {
  btn.addEventListener("click", () => btn.closest("dialog").close());
});

// Dashboard
async function loadDashboard() {
  try {
    const [libStats, prestStats] = await Promise.all([
      api("GET", "/libros/estadisticas"),
      api("GET", "/prestamos/estadisticas"),
    ]);

    document.getElementById("statLibros").textContent = libStats.data.total_libros;
    document.getElementById("statDisponibles").textContent =
      libStats.data.total_ejemplares_disponibles;
    document.getElementById("statActivos").textContent =
      prestStats.data.prestamos_activos;
    document.getElementById("statVencidos").textContent =
      prestStats.data.prestamos_vencidos;

    const chart = document.getElementById("categoriasChart");
    const cats = libStats.data.libros_por_categoria || [];
    const max = Math.max(...cats.map((c) => c.cantidad), 1);

    chart.innerHTML = cats.length
      ? cats
          .map(
            (c) => `
        <div class="category-bar">
          <span>${c.categoria}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${(c.cantidad / max) * 100}%"></div></div>
          <span>${c.cantidad}</span>
        </div>`
          )
          .join("")
      : '<p style="color:var(--text-muted)">No hay datos. Ejecuta <code>python seed.py</code> para cargar datos de prueba.</p>';
  } catch (e) {
    console.error(e);
  }
}

// Libros
let librosCache = [];

async function loadLibros(search = "") {
  try {
    const data = await api("GET", "/libros");
    librosCache = data.data;

    const q = search.trim().toLowerCase();
    const filtered = q
      ? librosCache.filter(
          (l) =>
            l.titulo.toLowerCase().includes(q) ||
            l.autor.toLowerCase().includes(q) ||
            (l.categoria && l.categoria.toLowerCase().includes(q)) ||
            l.isbn.toLowerCase().includes(q)
        )
      : librosCache;

    renderLibros(filtered);
  } catch (e) {
    toast(e.message, "error");
  }
}

function renderLibros(libros) {
  const tbody = document.getElementById("librosTable");
  if (!libros.length) {
    tbody.innerHTML =
      '<tr class="empty-row"><td colspan="8">No hay libros en el catálogo</td></tr>';
    return;
  }

  tbody.innerHTML = libros
    .map(
      (l) => `
    <tr>
      <td>${l.id}</td>
      <td><strong>${l.titulo}</strong></td>
      <td>${l.autor}</td>
      <td>${l.isbn}</td>
      <td>${l.categoria || "—"}</td>
      <td>${l.anio_publicacion}</td>
      <td>${l.cantidad_disponible}</td>
      <td>
        <button class="btn btn-sm btn-secondary" onclick="editLibro(${l.id})">Editar</button>
        <button class="btn btn-sm btn-danger" onclick="deleteLibro(${l.id})">Eliminar</button>
      </td>
    </tr>`
    )
    .join("");
}

let searchTimeout;
document.getElementById("searchInput").addEventListener("input", (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadLibros(e.target.value), 300);
});

document.getElementById("btnNuevoLibro").addEventListener("click", () => {
  document.getElementById("modalLibroTitle").textContent = "Nuevo libro";
  document.getElementById("formLibro").reset();
  document.getElementById("libroId").value = "";
  document.getElementById("modalLibro").showModal();
});

window.editLibro = function (id) {
  const libro = librosCache.find((l) => l.id === id);
  if (!libro) return;
  document.getElementById("modalLibroTitle").textContent = "Editar libro";
  document.getElementById("libroId").value = libro.id;
  document.getElementById("libroTitulo").value = libro.titulo;
  document.getElementById("libroAutor").value = libro.autor;
  document.getElementById("libroIsbn").value = libro.isbn;
  document.getElementById("libroEditorial").value = libro.editorial || "";
  document.getElementById("libroAnio").value = libro.anio_publicacion;
  document.getElementById("libroCategoria").value = libro.categoria || "";
  document.getElementById("libroCantidad").value = libro.cantidad_disponible;
  document.getElementById("modalLibro").showModal();
};

window.deleteLibro = async function (id) {
  if (!confirm("¿Eliminar este libro?")) return;
  try {
    await api("DELETE", `/libros/${id}`);
    toast("Libro eliminado");
    loadLibros();
    loadDashboard();
  } catch (e) {
    toast(e.message, "error");
  }
};

document.getElementById("formLibro").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("libroId").value;
  const payload = {
    titulo: document.getElementById("libroTitulo").value,
    autor: document.getElementById("libroAutor").value,
    isbn: document.getElementById("libroIsbn").value,
    editorial: document.getElementById("libroEditorial").value || null,
    anio_publicacion: parseInt(document.getElementById("libroAnio").value),
    categoria: document.getElementById("libroCategoria").value || null,
    cantidad_disponible: parseInt(document.getElementById("libroCantidad").value),
  };

  try {
    if (id) {
      await api("PUT", `/libros/${id}`, payload);
      toast("Libro actualizado");
    } else {
      await api("POST", "/libros", payload);
      toast("Libro creado");
    }
    document.getElementById("modalLibro").close();
    loadLibros();
    loadDashboard();
  } catch (e) {
    toast(e.message, "error");
  }
});

// Préstamos
let prestamosMode = "activos";

async function loadPrestamos(mode = prestamosMode) {
  prestamosMode = mode;
  try {
    const path = mode === "activos" ? "/prestamos/activos" : "/prestamos";
    const data = await api("GET", path);
    renderPrestamos(data.data);
  } catch (e) {
    toast(e.message, "error");
  }
}

function renderPrestamos(prestamos) {
  const tbody = document.getElementById("prestamosTable");
  if (!prestamos.length) {
    tbody.innerHTML =
      '<tr class="empty-row"><td colspan="8">No hay préstamos registrados</td></tr>';
    return;
  }

  tbody.innerHTML = prestamos
    .map((p) => {
      const vencido = isVencido(p);
      const estadoClass =
        p.estado === "devuelto" ? "badge-devuelto" : vencido ? "badge-vencido" : "badge-activo";
      const estadoText =
        p.estado === "devuelto" ? "Devuelto" : vencido ? "Vencido" : "Activo";
      const devolverBtn =
        p.estado === "activo"
          ? `<button class="btn btn-sm btn-success" onclick="devolverPrestamo(${p.id})">Devolver</button>`
          : "";

      return `
    <tr>
      <td>${p.id}</td>
      <td><strong>${p.libro_titulo || "—"}</strong><br><small>${p.libro_autor || ""}</small></td>
      <td>${p.nombre_usuario}</td>
      <td>${p.email}</td>
      <td>${formatDate(p.fecha_prestamo)}</td>
      <td>${formatDate(p.fecha_devolucion_esperada)}</td>
      <td><span class="badge ${estadoClass}">${estadoText}</span></td>
      <td>${devolverBtn}</td>
    </tr>`;
    })
    .join("");
}

document.getElementById("btnVerTodos").addEventListener("click", () => loadPrestamos("todos"));
document.getElementById("btnNuevoPrestamo").addEventListener("click", async () => {
  try {
    const data = await api("GET", "/libros");
    const select = document.getElementById("prestamoLibro");
    const disponibles = data.data.filter((l) => l.cantidad_disponible > 0);
    if (!disponibles.length) {
      toast("No hay libros disponibles para préstamo", "error");
      return;
    }
    select.innerHTML = disponibles
      .map(
        (l) =>
          `<option value="${l.id}">${l.titulo} — ${l.autor} (${l.cantidad_disponible} disp.)</option>`
      )
      .join("");
    document.getElementById("formPrestamo").reset();
    document.getElementById("prestamoDias").value = 14;
    document.getElementById("modalPrestamo").showModal();
  } catch (e) {
    toast(e.message, "error");
  }
});

window.devolverPrestamo = async function (id) {
  try {
    await api("PUT", `/prestamos/${id}/devolver`);
    toast("Libro devuelto correctamente");
    loadPrestamos();
    loadLibros();
    loadDashboard();
  } catch (e) {
    toast(e.message, "error");
  }
};

document.getElementById("formPrestamo").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    libro_id: parseInt(document.getElementById("prestamoLibro").value),
    nombre_usuario: document.getElementById("prestamoNombre").value,
    email: document.getElementById("prestamoEmail").value,
    dias_prestamo: parseInt(document.getElementById("prestamoDias").value) || 14,
  };

  try {
    await api("POST", "/prestamos", payload);
    toast("Préstamo registrado");
    document.getElementById("modalPrestamo").close();
    loadPrestamos();
    loadLibros();
    loadDashboard();
  } catch (e) {
    toast(e.message, "error");
  }
});

// Estado de la biblioteca
async function checkEstado() {
  const el = document.getElementById("apiStatus");
  try {
    const data = await api("GET", "/biblioteca/estado");
    el.className = "header-status online";
    el.querySelector("span:last-child").textContent = data.mensaje || "Biblioteca en línea";
  } catch {
    el.className = "header-status offline";
    el.querySelector("span:last-child").textContent = "Biblioteca desconectada";
  }
}

// Init
checkEstado();
loadDashboard();
loadLibros();
loadPrestamos("activos");

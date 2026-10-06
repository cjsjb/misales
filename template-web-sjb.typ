// template-web-sjb.typ — Hoja SJB para web (destino HTML).
//
// Se usa desde un archivo envoltorio, igual que template-sjb.typ. El envoltorio
// importa esta plantilla, los valores por omisión y el .inc del domingo, y llama
// a render-web-sjb(). Ejemplo de compilación:
//
//   typst compile --features html --format html --pretty \
//     --font-path fonts envoltorio.typ salida.html
//
// Diferencias con template-sjb.typ: sólo lo que tiene sentido en papel.
//   - Sin #set page (tamaño, márgenes, numeración) ni #pagebreak(): la
//     paginación no existe en HTML y el destino la rechaza.
//   - Sin #align() ni la regla decorativa del encabezado (grid + line): los
//     elementos de maquetación no sobreviven a la exportación a HTML.
//   - Sin los espaciados fijos de la portada (#v(...)).
//   - Los encabezados de nivel 1 se ocultan, igual que en papel.
//   - La presentación vive en styles.css (Typst no emite CSS): las clases que
//     se ven aquí (.cubierta, .cubierta-titulo, .respuesta, …) son el enganche.
#import "common.typ": con_respuestas

// En HTML, el color y la negrita que pide respuesta() (text(fill:) + weight:)
// no sobreviven a la exportación: Typst los descarta y el párrafo sale pelado
// («<p>Todos: Amén.</p>»). Por eso la respuesta se marca con una clase y el
// aspecto lo pone styles.css. La agrupación en párrafos no se repite: la hace
// con_respuestas(), que recibe esta función.
#let respuesta_web(texto) = html.elem("span", attrs: (class: "respuesta"))[#texto]

#let render-web-sjb(
  tiempo: "Ordinario",
  domingo_num: 0,
  ciclo: "A",
  fecha: none,
  hora: none,
  frase: none,
  oracion_colecta: none,
  lectura_primera_fuente: none,
  lectura_primera: none,
  salmo_fuente: none,
  salmo_partitura: none,
  salmo_aclamacion: none,
  salmo_estrofas: none,
  lectura_segunda_fuente: none,
  lectura_segunda: none,
  aleluya_fuente: none,
  aleluya_aclamacion: none,
  evangelio_fuente: none,
  evangelio: none,
  oracion_delosfieles: none,
  oracion_ofrendas: none,
  oracion_comunion: none,
) = {
  set text(lang: "es")

  // Los encabezados de nivel 1 («Ritos iniciales», «Liturgia de la palabra», …)
  // se ocultan, igual que en la versión impresa: agrupan, no se muestran.
  show heading.where(level: 1): it => none

  // Fecha larga en español: «Domingo 27 de septiembre de 2026».
  let dias_es = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")
  let meses_es = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
  )

  let fecha_dt = if fecha == none { none } else {
    let p = fecha.split("-")
    datetime(year: int(p.at(0)), month: int(p.at(1)), day: int(p.at(2)))
  }

  let dia_semana = if fecha_dt == none { none } else {
    dias_es.at(fecha_dt.weekday() - 1)
  }

  let fecha_larga = if fecha_dt == none { none } else {
    (
      dias_es.at(fecha_dt.weekday() - 1)
        + " " + str(fecha_dt.day())
        + " de " + meses_es.at(fecha_dt.month() - 1)
        + " de " + str(fecha_dt.year())
    )
  }

  // Números romanos: 26 → «XXVI».
  let romanos = (
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
  )

  let romano(n) = {
    let s = ""
    for (valor, letra) in romanos {
      let k = calc.floor(n / valor)
      s += letra * k
      n -= k * valor
    }
    s
  }

  // Título de la pestaña del navegador y de la ficha del enlace.
  let subtitulo = if fecha_larga == none { "" } else { " — " + fecha_larga }
  set document(title: "Domingo " + romano(domingo_num) + " del tiempo " + tiempo + subtitulo)

  [
    // La hoja de estilos vive junto al HTML. Se enlaza aquí, y no en <head>,
    // para no tener que apropiarnos de <html>/<head>/<body>; si más adelante
    // hace falta controlar <title> y los metadatos, se puede tomar el <head>.
    #html.elem("link", attrs: (rel: "stylesheet", href: "styles.css"))

    // La cubierta iba dentro de #align(): los elementos de maquetación no
    // sobreviven a la exportación a HTML y se llevan su contenido por delante,
    // así que la alineación la hace styles.css a través de estas clases.
    #html.elem("div", attrs: (class: "cubierta"))[
      #image("logo-sjb.png", width: 3cm)

      #html.elem("p", attrs: (class: "cubierta-titulo"))[
        #upper[#romano(domingo_num) #dia_semana DEL TIEMPO #tiempo]
      ]

      #html.elem("p", attrs: (class: "cubierta-fecha"))[#fecha_larga]

      #html.elem("p", attrs: (class: "cubierta-frase"))[#emph(frase)]

      #image("lema-2026.png", width: 10cm)
    ]

    = Ritos iniciales

    == Oración colecta

    #oracion_colecta #respuesta_web[Amén.]

    = Liturgia de la palabra

    == Primera lectura

    #lectura_primera_fuente

    #lectura_primera

    Palabra de Dios. \
    #respuesta_web[Te alabamos, Señor.]

    == Salmo responsorial

    #salmo_fuente

    #if salmo_estrofas != none {
      respuesta_web(salmo_aclamacion)
      parbreak()
      for estrofa in salmo_estrofas [
        #parbreak()
        #estrofa
        #parbreak()
        #respuesta_web(salmo_aclamacion)
      ]
    }

    == Segunda lectura

    #lectura_segunda_fuente

    #lectura_segunda

    Palabra de Dios. \
    #respuesta_web[Te alabamos, Señor.]

    == Aclamación antes del evangelio

    #aleluya_fuente

    #respuesta_web[Aleluya, aleluya.]

    #aleluya_aclamacion

    #respuesta_web[Aleluya, aleluya.]

    == Evangelio

    #evangelio_fuente

    #evangelio

    Palabra del Señor. \
    #respuesta_web[Gloria a ti, Señor Jesús.]

    == Oración universal

    #con_respuestas(oracion_delosfieles, respuesta_fn: respuesta_web)

    = Liturgia eucarística

    == Oración sobre las ofrendas

    #oracion_ofrendas #respuesta_web[Amén.]

    == Oración después de la comunión

    #oracion_comunion #respuesta_web[Amén.]

    = Rito de conclusión
  ]
}

// template-sjb.typ
#import "common.typ": respuesta, con_respuestas, canto

#let render-sjb(
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
  set page(
    width: 7in,
    height: 8.5in,
    margin: (inside: 0.5in, outside: 0.5in, top: 1.0cm, bottom: 0.75cm),
    numbering: "1",
  )

  set text(
    font: ("Droid Serif"),
    size: 12pt,
    lang: "es"
  )

  set par(
    justify: true,
    leading: 0.65em,
  )

  show heading.where(level: 1): it => none

  show heading.where(level: 2): it => pad(bottom: -0.25em)[
    #grid(
      columns: (auto, 1fr),
      column-gutter: 0.0em,
      align: horizon,
      text(
        font: ("Montserrat"),
        fill: rgb("#2a6099"),
        weight: "bold",
        size: 14pt,
        upper(it.body),
      ),
      line(length: 100%, stroke: 1.25pt + rgb("#2a6099")),
    )
  ]

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

  [
    #set page(numbering: none)
    #align(center)[
      #image("header-sjb.png", width: 11.1cm)

      #v(2em)

      #text(font: ("Montserrat"), weight: "bold", size: 25pt)[
        #upper[
          #romano(domingo_num) #dia_semana DEL\
          TIEMPO #tiempo
        ]
      ]

      #text(font: ("Montserrat"), size: 18pt, fill: rgb("#00a933"))[#fecha_larga]

      #v(5em)

      #text(font: ("Montserrat"), size: 15pt)[#emph(frase)]

      #v(6em)

      #image("lema-2026.png", width: 10cm)
    ]

    #pagebreak()
    #set page(numbering: "1")

    = Ritos iniciales

    == Oración colecta

    #oracion_colecta #respuesta[Amén.]

    = Liturgia de la palabra

    == Primera lectura

    #lectura_primera_fuente

    #lectura_primera

    Palabra de Dios. \
    #respuesta[Te alabamos, Señor.]

    == Salmo responsorial

    #salmo_fuente

    #if salmo_estrofas != none {
      respuesta(salmo_aclamacion)
      parbreak()
      for estrofa in salmo_estrofas [
        #parbreak()
        #estrofa
        #parbreak()
        #respuesta(salmo_aclamacion)
      ]
    }

    == Segunda lectura

    #lectura_segunda_fuente

    #lectura_segunda

    Palabra de Dios. \
    #respuesta[Te alabamos, Señor.]

    == Aclamación antes del evangelio

    #aleluya_fuente

    #respuesta[Aleluya, aleluya.]

    #aleluya_aclamacion

    #respuesta[Aleluya, aleluya.]

    == Evangelio

    #evangelio_fuente

    #evangelio

    Palabra del Señor. \
    #respuesta[Gloria a ti, Señor Jesús.]

    == Oración universal

    #con_respuestas(oracion_delosfieles)

    = Liturgia eucarística

    == Oración sobre las ofrendas

    #oracion_ofrendas #respuesta[Amén.]

    == Oración después de la comunión

    #oracion_comunion #respuesta[Amén.]

    = Rito de conclusión
  ]
}

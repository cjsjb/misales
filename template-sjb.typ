// template-sjb.typ
#import "common.typ": respuesta, con_respuestas, canto, dia_semana, fecha_larga, mes_capital, separador_fecha

#let cabecera_reflexion(icono, titulo, ambos_lados: true) = {
  let azul = rgb("#2a6099")
  let tam_icono = 1.5cm
  let titulo_txt = text(
    font: "Montserrat",
    weight: "bold",
    size: 18pt,
    fill: azul,
    upper(titulo),
  )
  let fila = if ambos_lados {
    grid(
      columns: (auto, auto, auto),
      column-gutter: 2em,
      align: horizon,
      image(icono, width: tam_icono),
      titulo_txt,
      image(icono, width: tam_icono),
    )
  } else {
    grid(
      columns: (auto, 1fr),
      column-gutter: 0.6em,
      align: horizon,
      image(icono, width: tam_icono),
      align(center, titulo_txt),
    )
  }
  pad(top: 1.0em, bottom: 0.5em, grid(
    columns: (1fr,),
    row-gutter: 0.55em,
    align: center,
    // Separador: tres puntos, dibujados como círculos para no depender de la
    // fuente.
    grid(
      columns: (auto,) * 3,
      column-gutter: 0.3cm,
      ..((circle(radius: 0.55mm, fill: azul),) * 3),
    ),
    fila,
  ))
}

#let render-sjb(
  tiempo: "Ordinario",
  domingo_num: 0,
  ciclo: "A",
  fecha: none,
  hora: none,
  frase: none,
  ocasion: none,
  color_liturgico: none,
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
  oracion_personal: none,
  eco_de_la_palabra: none,
  // El misal mensual llama a esta plantilla una vez por día: sólo el primero
  // lleva portada; los demás abren con el separador de fecha.
  portada: true,
  separador: false,
  // Portada de cuaderno mensual: «Misal Mensual» y el mes, en vez del día
  // litúrgico y la fecha. Sólo la pone haz-misal-mensual.py, en el primer día.
  mensual: false,
) = {
  // La página y el texto del misal los aplica ajustes_misal, de common.typ, con
  // un show rule al principio del documento (AJUSTES_MISAL en haz-misal.py). No
  // pueden vivir aquí: cada `set page` que entra en vigor inserta una página
  // nueva, así que con esta plantilla llamada una vez por día el misal mensual
  // abría página en cada día.

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

  // El día de la semana y la fecha larga los da common.typ: los usan también la
  // hoja web y el separador del misal mensual.

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
    // Color litúrgico de la fecha: lo resuelve generate_inc.py (la sección
    // `Color` de la liturgia o, si falta, el tiempo litúrgico). El blanco se
    // imprime en negro, que si no no se vería sobre el papel. Ojo: este bloque
    // es contenido, así que el código va con #.
    #let paleta_liturgica = (
      verde: rgb("#00a933"),
      morado: rgb("#5b2d8e"),
      blanco: black,
      rojo: rgb("#b3252c"),
    )
    #let color_fecha = paleta_liturgica.at(color_liturgico, default: paleta_liturgica.verde)

    // Dentro del misal mensual la portada es la del primer día: los demás la
    // saltan, pero el separador lo lleva también el primero, después de ella. La
    // numeración del cuerpo vuelve sola al cerrarse este bloque, con el valor de
    // ajustes_misal (common.typ).
    #if portada [
    #set page(numbering: none)
    #align(center)[
      #image("header-sjb.png", width: 11.1cm)

      #v(2em)

      // El cuaderno del mes lleva portada propia: ni el día litúrgico ni la
      // fecha, sólo el título del cuaderno y el mes. El misal diario se queda
      // con la de siempre.
      #if mensual [
        #text(font: ("Montserrat"), weight: "bold", size: 25pt)[Misal Mensual]

        #text(font: ("Montserrat"), size: 18pt, fill: color_fecha)[#mes_capital(fecha)]
      ] else [
        #text(font: ("Montserrat"), weight: "bold", size: 25pt)[
          #upper[
            #romano(domingo_num) #dia_semana(fecha) DEL\
            TIEMPO #tiempo
          ]
        ]

        #text(font: ("Montserrat"), size: 18pt, fill: color_fecha)[#fecha_larga(fecha)]
      ]

      // La ocasión va en la línea siguiente y en negro: el color litúrgico lo
      // lleva la fecha. generate_inc.py no la trae si el día es ordinario.
      //
      // En el cuaderno del mes no va: esa ocasión es la del día 1, no la del mes.
      #if ocasion != none and not mensual [
        #text(font: ("Montserrat"), size: 14pt, fill: black)[#ocasion]
      ]

      #v(5em)

      #text(font: ("Montserrat"), size: 15pt)[#emph(frase)]

      #v(6em)

      #image("lema-2026.png", width: 10cm)
    ]

    #pagebreak()
    ]

    // El separador va aquí dentro, y no en el envoltorio, para que herede el
    // tamaño de página y el tipo del misal.
    //
    // Sin salto de página a propósito: el misal mensual es un texto continuo y
    // el separador es lo único que marca dónde empieza cada día.
    #if separador [
      #separador_fecha(
        fecha,
        [#dia_semana(fecha) #romano(domingo_num) DEL TIEMPO #tiempo],
        ocasion: ocasion,
        color: color_fecha,
      )
    ]

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

    // En las ferias no hay segunda lectura: si falta, se oculta la sección
    // entera, con su salutación final.
    #if lectura_segunda_fuente != none [
      == Segunda lectura

      #lectura_segunda_fuente

      #lectura_segunda

      Palabra de Dios. \
      #respuesta[Te alabamos, Señor.]
    ]

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

    // La oración universal es opcional: si falta, se oculta la sección.
    #if oracion_delosfieles != none [
      == Oración universal

      #con_respuestas(oracion_delosfieles)
    ]

    = Liturgia eucarística

    == Oración sobre las ofrendas

    #oracion_ofrendas #respuesta[Amén.]

    == Oración después de la comunión

    #oracion_comunion #respuesta[Amén.]

    #if oracion_personal != none [
      == Oración personal después de comulgar

      #oracion_personal
    ]

    #if eco_de_la_palabra != none [
      #cabecera_reflexion("icono-ecodelapalabra-bw.svg", "Eco de la palabra")

      #eco_de_la_palabra
    ]

    = Rito de conclusión
  ]
}

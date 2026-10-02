// template-cjsjb.typ
#import "common.typ": respuesta, con_respuestas, canto

#let render-cjsjb(
  tiempo: "Ordinario",
  domingo_num: 0,
  ciclo: "A",
  fecha: none,
  hora: none,
  frase: none,
  canto_entrada: none,
  canto_sennortenpiedad: none,
  canto_gloria: none,
  canto_aleluya: none,
  canto_ofertorio: none,
  canto_santo: none,
  canto_corderodedios: none,
  canto_comunion: none,
  canto_postcomunion: none,
  canto_salida: none,
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
  monicion_entrada: none,
  monicion_ofrendas: none,
) = {
  set page(
    width: 5.5in,
    height: 8.5in,
    margin: (inside: 0.5cm, outside: 0.5cm, top: 0.5cm, bottom: 0.5cm),
    numbering: "1",
  )

  set text(
    font: ("Roboto"),
    size: 10pt,
    lang: "es"
  )

  set par(
    justify: true,
    leading: 0.65em,
  )

  show heading.where(level: 1): it => context {
    set text(fill: black, size: 16.8pt)
    block(
      width: 100%,
      stroke: 0.75pt + black,
      inset: 0.25em,
      smallcaps(it.body)
    )
  }

  show heading.where(level: 2): it => pad(bottom: 0.5em)[
    #set text(fill: rgb("#2a6099"), weight: "bold", size: 14pt)
    #upper(it.body)
  ]

  [
    Domingo #domingo_num del tiempo #tiempo

    = Ritos iniciales

    == Monición de entrada

    #monicion_entrada

    == Entrada

    #canto(canto_entrada)

    En el nombre del Padre, y del Hijo, y del Espíritu Santo.

    #respuesta[Amén.]

    == Saludo

    La gracia de nuestro Señor Jesucristo, el amor del Padre y la comunión del Espíritu Santo estén con todos ustedes.

    La gracia y la paz de parte de Dios, nuestro Padre, y de Jesucristo, el Señor, estén con todos ustedes.

    El Señor esté con ustedes.

    #respuesta[Y con tu espíritu.]

    == Acto penitencial

    #canto(canto_sennortenpiedad)

    == Gloria

    #canto(canto_gloria)

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

    #if salmo_partitura != none {
      if type(salmo_partitura) == str {
        image(salmo_partitura, height: 1.25cm)
      } else {
        salmo_partitura
      }
    }

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

    #canto(canto_aleluya)

    #aleluya_fuente

    #aleluya_aclamacion

    == Evangelio

    El Señor esté con ustedes.

    #respuesta[Y con tu espíritu.]

    #evangelio_fuente

    #respuesta[Gloria a ti, Señor.]

    #evangelio

    Palabra del Señor. \
    #respuesta[Gloria a ti, Señor Jesús.]

    == Profesión de fe

    #respuesta[
      Creo en un solo Dios, Padre todopoderoso,
      Creador del cielo y de la tierra,
      de todo lo visible y lo invisible.

      Creo en un solo Señor, Jesucristo,
      Hijo único de Dios, nacido del Padre antes de todos los siglos:
      Dios de Dios, Luz de Luz, Dios verdadero de Dios verdadero,
      engendrado, no creado, de la misma naturaleza del Padre,
      por quien todo fue hecho;
      que por nosotros lo hombres,
      y por nuestra salvación bajó del cielo,
      y por obra del Espíritu Santo se encarnó de María, la Virgen,
      y se hizo hombre;
      y por nuestra causa fue crucificado
      en tiempos de Poncio Pilato;
      padeció y fue sepultado,
      y resucitó al tercer día, según las Escrituras,
      y subió al cielo,
      y está sentado a la derecha del Padre;
      y de nuevo vendrá con gloria
      para juzgar a vivos y muertos,
      y su reino no tendrá fin.

      Creo en el Espíritu Santo,
      Señor y dador de vida,
      que procede del Padre y del Hijo,
      que con el Padre y el Hijo
      recibe una misma adoración y gloria,
      y que habló por los profetas.

      Creo en la Iglesia, que es una, santa, católica y apostólica.

      Confieso que hay un solo bautismo
      para el perdón de los pecados.

      Espero la resurrección de los muertos
      y la vida del mundo futuro.

      Amén.
    ]

    == Oración universal

    #con_respuestas(oracion_delosfieles)

    = Liturgia eucarística

    == Monición de ofrendas

    #monicion_ofrendas

    == Ofertorio

    #canto(canto_ofertorio)

    == Oración sobre las ofrendas

    #oracion_ofrendas #respuesta[Amén.]

    == Plegaria eucarística

    == Santo

    #canto(canto_santo)

    == Fracción del pan

    #canto(canto_corderodedios)

    == Comunión

    #canto(canto_comunion)

    #canto(canto_postcomunion)

    == Oración después de la comunión

    #oracion_comunion #respuesta[Amén.]

    = Rito de conclusión

    == Bendición

    == Salida

    #canto(canto_salida)
  ]
}

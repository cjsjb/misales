// common.typ

#let respuesta(texto) = {
  text(
    rgb("#5983b0"),
    weight: "bold",
    [#texto]
  )
}

#let empieza_con_todos(parrafo) = {
  let partes = ()
  for hijo in parrafo {
    let t = hijo.at("text", default: none)
    if t != none and type(t) == str {
      partes.push(t)
      if partes.len() >= 3 { break }
    }
  }
  partes.join("").starts-with("Todos:")
}

// El aspecto de cada respuesta lo pone respuesta_fn. En papel es respuesta()
// (text(fill:) + weight:); en la web es una variante que emite una clase,
// porque la exportación a HTML descarta el fill y el weight y el párrafo sale
// pelado. Se pasa desde la plantilla en vez de decidirlo aquí mirando el
// destino con target() a propósito: target() y el módulo html sólo existen si
// se compila con --features html, y sin esa opción nombrar html es un error de
// compilación («cannot access variable `html` because the `html` feature is not
// enabled»). Este archivo también lo compilan las plantillas de papel, que no
// pasan esa opción, así que la diferencia por destino tiene que elegirse desde
// la plantilla. La agrupación por párrafos, que es lo que se repetía, sí es
// común.
#let con_respuestas(contenido, respuesta_fn: respuesta) = {
  if contenido == none { return none }
  let hijos = if contenido.has("children") { contenido.children } else { (contenido,) }
  let parrafos = ()
  let actual = ()
  for hijo in hijos {
    if hijo.func() == parbreak {
      if actual.len() > 0 { parrafos.push(actual) }
      actual = ()
    } else {
      actual.push(hijo)
    }
  }
  if actual.len() > 0 { parrafos.push(actual) }

  let salida = ()
  for i in range(parrafos.len()) {
    let parrafo = parrafos.at(i)
    let cuerpo = parrafo.join()
    if i > 0 { salida.push(parbreak()) }
    if empieza_con_todos(parrafo) {
      salida.push(respuesta_fn(cuerpo))
    } else {
      salida.push(cuerpo)
    }
  }
  salida.join()
}

#let canto(contenido) = {
  if contenido == none { return none }
  let literal(t) = t.replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")
  let estrofas = ()
  let actual = ()
  for linea in contenido.split("\n") {
    if linea.trim() == "" {
      if actual.len() > 0 { estrofas.push(actual) }
      actual = ()
    } else {
      actual.push(linea.trim())
    }
  }
  if actual.len() > 0 { estrofas.push(actual) }
  if estrofas.len() == 0 { return none }

  let verso_de(lineas) = {
    let r = ()
    for i in range(lineas.len()) {
      if i > 0 { r.push(linebreak()) }
      r.push(eval(literal(lineas.at(i)), mode: "markup"))
    }
    r.join()
  }

  let salida = ()
  for i in range(estrofas.len()) {
    let lineas = estrofas.at(i)
    if i == 0 {
      salida.push(text(eval(literal(lineas.at(0)), mode: "markup"), weight: "bold"))
      let resto = lineas.slice(1)
      if resto.len() > 0 {
        salida.push(parbreak())
        salida.push(verso_de(resto))
      }
    } else {
      salida.push(parbreak())
      salida.push(verso_de(lineas))
    }
  }

  block(
    salida.join(),
    width: 100%,
    fill: rgb("#eeeeee"),
    inset: (x: 0.7em, y: 0.5em),
    radius: 2pt,
    breakable: true,
  )
}

// Fecha larga en español: «Martes 6 de octubre de 2026». Vive aquí, y no en cada
// plantilla, porque la usan la cubierta de papel, la de la web y el separador
// del misal mensual; antes estaba copiada en las dos plantillas.
#let dias_es = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")
// Con mayúscula, que es como sale en la portada del mensual; quien los quiera en
// minúscula —dentro de una frase— los pasa por lower().
#let meses_es = (
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)

#let fecha_dt(fecha) = {
  let p = fecha.split("-")
  datetime(year: int(p.at(0)), month: int(p.at(1)), day: int(p.at(2)))
}

// Sin fecha —una plantilla que no la pase— devuelve none, como antes: en
// contenido, none no pinta nada.
#let dia_semana(fecha) = {
  if fecha == none { return none }
  dias_es.at(fecha_dt(fecha).weekday() - 1)
}

#let fecha_larga(fecha) = {
  if fecha == none { return none }
  let d = fecha_dt(fecha)
  // Los paréntesis no son decorativos: fuera de ellos Typst corta la expresión
  // en cada salto de línea y el «+» de la línea siguiente queda como un más
  // unario sobre una cadena («cannot apply unary '+' to string»).
  (
    dias_es.at(d.weekday() - 1)
      + " " + str(d.day())
      + " de " + lower(meses_es.at(d.month() - 1))
      + " de " + str(d.year())
  )
}

// Separador entre los misales de un mismo mes (lo usa haz-misal-mensual.py): la
// fecha del día con el mismo aire que los epígrafes de sección, para que se lea
// como parte del misal y no como un añadido. No abre página: cae donde acaba el
// día anterior, así que el aire de arriba es lo que lo separa de él.
// Ajustes del misal impreso: tamaño de página, márgenes, numeración, fuente y
// justificado.
//
// Se aplican con un show rule al principio del documento, y no dentro de
// template-sjb.typ, por una regla de Typst: cada `set page` que entra en vigor
// inserta una página nueva, aunque los valores sean los mismos que ya había. Con
// la plantilla llamada una vez por día, eso abría página en cada día del misal
// mensual, y como el primer contenido del día es el separador de fecha, el
// separador salía siempre arriba de una página nueva.
//
// Uso, como primeras líneas del documento:
//   #import "common.typ": ajustes_misal
//   #show: ajustes_misal
//
// Lo piden el envoltorio del misal diario y el maestro del mensual, cada uno una
// sola vez (AJUSTES_MISAL en haz-misal.py).
#let ajustes_misal(doc) = {
  set page(
    width: 7in,
    height: 8.5in,
    margin: (inside: 0.5in, outside: 1.0cm, top: 1.0cm, bottom: 0.75cm),
    numbering: "1",
  )

  set text(
    font: ("Droid Serif"),
    size: 11pt,
    lang: "es"
  )

  set par(
    justify: true,
    leading: 0.65em,
  )

  doc
}

// Fecha del día en corto, para el separador del misal mensual: «4 de octubre».
#let fecha_dia_mes(fecha) = {
  if fecha == none { return none }
  let d = fecha_dt(fecha)
  str(d.day()) + " de " + lower(meses_es.at(d.month() - 1))
}

// El mes suelto y con mayúscula: «Octubre». Es lo que lleva la portada del
// cuaderno del mes, en lugar de la fecha.
#let mes_capital(fecha) = {
  if fecha == none { return none }
  meses_es.at(fecha_dt(fecha).month() - 1)
}

// Separador entre los misales de un mismo mes (lo usa haz-misal-mensual.py): la
// fecha y, debajo, la banda con el día —día de la semana, ordinal y tiempo, más
// la ocasión si la hay— en el color litúrgico, con filete arriba. El
// blanco llega ya convertido en negro, como en el resto del misal impreso.
//
// No abre página: cae donde acaba el día anterior, así que el aire de arriba es
// lo que lo separa de él.
//
// Va entero en una sola página (breakable: false): el filete, la fecha y
// la banda son una pieza, y sin eso se repartían entre páginas distintas. Si no
// cabe al final de una, pasa entero a la siguiente.
//
// El título lo arma template-sjb.typ, que ya tiene el día resuelto (romano,
// dia_semana, tiempo, ocasión) y el color de la fecha en color_fecha.
#let separador_fecha(fecha, titulo, ocasion: none, color: rgb("#2a6099")) = {
  let azul = rgb("#2a6099")
  block(width: 100%, breakable: false, pad(top: 0.3em, bottom: 0.1em, [
    #line(length: 100%, stroke: 1.25pt + azul)

    #align(center)[
      #text(font: ("Montserrat"), weight: "bold", size: 14pt, fill: azul)[#fecha_dia_mes(fecha)]
    ]

    #block(width: 100%, inset: (y: 0.5em), fill: color)[
      #align(center)[
        #text(font: ("Montserrat"), weight: "bold", size: 16pt, fill: white)[#upper(titulo)]
        #if ocasion != none [
          #linebreak()
          #text(font: ("Montserrat"), weight: "bold", size: 14pt, fill: white)[#upper(ocasion)]
        ]
      ]
    ]

  ]))
}

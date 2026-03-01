import type { Battle } from "./types"

export const battles: Battle[] = [
  {
    id: "1",
    title: "Chuty vs Aczino",
    mc1: { name: "Chuty", avatar: "C" },
    mc2: { name: "Aczino", avatar: "A" },
    participants: [
      { id: 1, name: "Chuty", avatar: "C", teamNumber: 0, positionInTeam: 0 },
      { id: 2, name: "Aczino", avatar: "A", teamNumber: 1, positionInTeam: 0 },
    ],
    battleFormat: "1v1" as const,
    videoUrl: "",
    youtubeUrl: "https://www.youtube.com/watch?v=ByC3sRdL_Xg",
    thumbnail: "",
    date: "2024-12-15",
    event: "God Level Fest 2024",
    rounds: 3,
    rhymes: [
      {
        id: "1-1",
        text: "Vengo desde el underground, no necesito el mainstream, mis barras son tan letales que dejan huella en tu stream",
        mc: "mc1",
        timestamp: 15,
        round: 1,
        ratings: { rima: 4.2, ingenio: 3.8, punchline: 4.0, respuesta: 3.5 },
      },
      {
        id: "1-2",
        text: "Tu carrera es como un chiste sin gracia, un payaso en la tarima que solo genera desgracia",
        mc: "mc2",
        timestamp: 32,
        round: 1,
        ratings: { rima: 4.5, ingenio: 4.2, punchline: 4.8, respuesta: 4.0 },
      },
      {
        id: "1-3",
        text: "Dices que eres el mejor pero tu flow es predecible, cada vez que subes al escenario es algo horrible",
        mc: "mc1",
        timestamp: 55,
        round: 1,
        ratings: { rima: 3.8, ingenio: 3.5, punchline: 3.2, respuesta: 3.9 },
      },
      {
        id: "1-4",
        text: "Mis palabras cortan como navaja en la noche, mientras tu rapeas dormido yo te paso por encima en un Porsche",
        mc: "mc2",
        timestamp: 78,
        round: 1,
        ratings: { rima: 4.7, ingenio: 4.5, punchline: 4.9, respuesta: 4.3 },
      },
      {
        id: "1-5",
        text: "Segundo round y ya te tiemblan las rodillas, mi lirica es fuego mientras la tuya solo brilla por su sencilla",
        mc: "mc1",
        timestamp: 120,
        round: 2,
        ratings: { rima: 4.0, ingenio: 4.1, punchline: 3.7, respuesta: 4.2 },
      },
      {
        id: "1-6",
        text: "Hablas de fuego pero solo prendes velas, yo prendo el escenario entero con mis barras paralelas",
        mc: "mc2",
        timestamp: 145,
        round: 2,
        ratings: { rima: 4.8, ingenio: 4.6, punchline: 4.5, respuesta: 4.7 },
      },
      {
        id: "1-7",
        text: "En el tercer round ya no te quedan recursos, yo sigo improvisando mientras tu lees tus discursos",
        mc: "mc1",
        timestamp: 200,
        round: 3,
        ratings: { rima: 4.3, ingenio: 4.4, punchline: 4.1, respuesta: 4.0 },
      },
      {
        id: "1-8",
        text: "La corona es mia, no la presto ni la alquilo, tu solo eres un rimador de bajo perfilo",
        mc: "mc2",
        timestamp: 225,
        round: 3,
        ratings: { rima: 4.6, ingenio: 4.3, punchline: 4.7, respuesta: 4.5 },
      },
    ],
  },
  {
    id: "2",
    title: "Skone vs Bnet",
    mc1: { name: "Skone", avatar: "S" },
    mc2: { name: "Bnet", avatar: "B" },
    participants: [
      { id: 3, name: "Skone", avatar: "S", teamNumber: 0, positionInTeam: 0 },
      { id: 4, name: "Bnet", avatar: "B", teamNumber: 1, positionInTeam: 0 },
    ],
    battleFormat: "1v1" as const,
    videoUrl: "",
    youtubeUrl: "https://www.youtube.com/watch?v=PiUOlHQJEfE",
    thumbnail: "",
    date: "2024-11-20",
    event: "FMS Internacional 2024",
    rounds: 2,
    rhymes: [
      {
        id: "2-1",
        text: "Llego el rey de las metricas, el que convierte las letras en electricas, mis rimas son mas que retorica",
        mc: "mc1",
        timestamp: 10,
        round: 1,
        ratings: { rima: 4.4, ingenio: 4.0, punchline: 3.9, respuesta: 3.6 },
      },
      {
        id: "2-2",
        text: "Rey sin corona, payaso sin carpa, cada barra que tiro te destroza y te aplasta",
        mc: "mc2",
        timestamp: 28,
        round: 1,
        ratings: { rima: 4.1, ingenio: 4.3, punchline: 4.5, respuesta: 4.2 },
      },
      {
        id: "2-3",
        text: "Mi ingenieria lirica supera tu existencia, no confundas mi paciencia con falta de potencia",
        mc: "mc1",
        timestamp: 50,
        round: 1,
        ratings: { rima: 4.6, ingenio: 4.7, punchline: 4.2, respuesta: 4.1 },
      },
      {
        id: "2-4",
        text: "Potencia dice el que se queda sin aliento, yo rapeo como el viento y tu te mueves muy lento",
        mc: "mc2",
        timestamp: 72,
        round: 1,
        ratings: { rima: 4.3, ingenio: 4.1, punchline: 4.4, respuesta: 4.6 },
      },
      {
        id: "2-5",
        text: "Segundo asalto y te voy a dar la clase, mi vocabulario es infinito, el tuyo no tiene base",
        mc: "mc1",
        timestamp: 115,
        round: 2,
        ratings: { rima: 4.0, ingenio: 3.8, punchline: 3.7, respuesta: 4.3 },
      },
      {
        id: "2-6",
        text: "Tu clase se la das a los que no saben nada, yo ya me gradue en la escuela de la calle brava",
        mc: "mc2",
        timestamp: 138,
        round: 2,
        ratings: { rima: 4.5, ingenio: 4.4, punchline: 4.6, respuesta: 4.8 },
      },
    ],
  },
  {
    id: "3",
    title: "Wos vs Rapder",
    mc1: { name: "Wos", avatar: "W" },
    mc2: { name: "Rapder", avatar: "R" },
    participants: [
      { id: 5, name: "Wos", avatar: "W", teamNumber: 0, positionInTeam: 0 },
      { id: 6, name: "Rapder", avatar: "R", teamNumber: 1, positionInTeam: 0 },
    ],
    battleFormat: "1v1" as const,
    videoUrl: "",
    youtubeUrl: "https://www.youtube.com/watch?v=qGTNx9cPm7U",
    thumbnail: "",
    date: "2025-01-10",
    event: "Red Bull Final Nacional",
    rounds: 3,
    rhymes: [
      {
        id: "3-1",
        text: "Desde Buenos Aires vine a conquistar la cima, cada barra que construyo es una obra prima",
        mc: "mc1",
        timestamp: 12,
        round: 1,
        ratings: { rima: 4.5, ingenio: 4.3, punchline: 4.1, respuesta: 3.8 },
      },
      {
        id: "3-2",
        text: "Obra prima dice pero pinta como un boceto, yo soy el artista completo que te deja obsoleto",
        mc: "mc2",
        timestamp: 30,
        round: 1,
        ratings: { rima: 4.7, ingenio: 4.8, punchline: 4.6, respuesta: 4.5 },
      },
      {
        id: "3-3",
        text: "Mi estilo es unico, no lo encuentras en Google, rapeo con el alma mientras tu buscas en Youtube",
        mc: "mc1",
        timestamp: 55,
        round: 1,
        ratings: { rima: 4.2, ingenio: 4.5, punchline: 4.0, respuesta: 3.7 },
      },
      {
        id: "3-4",
        text: "Youtube me hizo grande, las redes me hicieron leyenda, mientras tu sigues buscando que alguien tu musica entienda",
        mc: "mc2",
        timestamp: 78,
        round: 1,
        ratings: { rima: 4.4, ingenio: 4.2, punchline: 4.3, respuesta: 4.6 },
      },
      {
        id: "3-5",
        text: "Round dos y me transformo, soy otro nivel hermano, lo que hago con las palabras no lo hace ningun humano",
        mc: "mc1",
        timestamp: 120,
        round: 2,
        ratings: { rima: 4.6, ingenio: 4.4, punchline: 4.5, respuesta: 4.2 },
      },
      {
        id: "3-6",
        text: "Ningun humano dice pero yo si soy divino, cada verso que te lanzo te desvia del camino",
        mc: "mc2",
        timestamp: 142,
        round: 2,
        ratings: { rima: 4.8, ingenio: 4.7, punchline: 4.9, respuesta: 4.4 },
      },
      {
        id: "3-7",
        text: "Tercer round, minuto final, voy a dejar mi marca, mi legado en el freestyle es mas fuerte que una barca",
        mc: "mc1",
        timestamp: 195,
        round: 3,
        ratings: { rima: 4.1, ingenio: 4.0, punchline: 3.9, respuesta: 4.3 },
      },
      {
        id: "3-8",
        text: "Barca que se hunde con tu flow de principiante, yo soy el comandante, el MC mas brillante",
        mc: "mc2",
        timestamp: 218,
        round: 3,
        ratings: { rima: 4.5, ingenio: 4.6, punchline: 4.7, respuesta: 4.8 },
      },
      {
        id: "3-9",
        text: "No me importa lo que digas porque el publico decide, mi freestyle es una droga y tu flow ya no compite",
        mc: "mc1",
        timestamp: 240,
        round: 3,
        ratings: { rima: 4.3, ingenio: 4.2, punchline: 4.4, respuesta: 4.1 },
      },
      {
        id: "3-10",
        text: "El publico decide y decidio que soy el primero, tu eras el contendiente pero yo soy el verdadero",
        mc: "mc2",
        timestamp: 258,
        round: 3,
        ratings: { rima: 4.9, ingenio: 4.5, punchline: 4.8, respuesta: 4.9 },
      },
    ],
  },
]

export function getBattleById(id: string): Battle | undefined {
  return battles.find((b) => b.id === id)
}

export function getAverageScore(ratings: { rima: number; ingenio: number; punchline: number; respuesta: number }): number {
  return Number(((ratings.rima + ratings.ingenio + ratings.punchline + ratings.respuesta) / 4).toFixed(1))
}

export function getBattleAverageScore(battle: Battle): number {
  if (battle.rhymes.length === 0) return 0
  const total = battle.rhymes.reduce((acc, rhyme) => acc + getAverageScore(rhyme.ratings), 0)
  return Number((total / battle.rhymes.length).toFixed(1))
}

export function formatTimestamp(seconds: number): string {
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return `${min}:${sec.toString().padStart(2, "0")}`
}

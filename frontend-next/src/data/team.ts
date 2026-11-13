export type TeamMember = {
  id: string;
  name: string;
  contribution: string;
  description: string;
  photo: `/team/${string}.jpg`;
  linkedin: `https://${string}`;
  github?: `https://${string}`;
};

export const team: readonly TeamMember[] = [
  {
    id: "vinicius-morales",
    name: "Vinícius Morales",
    contribution: "Backend e IA",
    description: "Da lógica do backend à inteligência por trás dos dados.",
    photo: "/team/vinicius.jpg",
    linkedin: "https://www.linkedin.com/in/vin%C3%ADcius-morales-609744368/",
    github: "https://github.com/ViniciusMorales",
  },
  {
    id: "ana-furlaneto",
    name: "Ana Furlaneto",
    contribution: "Frontend e UI/UX",
    description: "Transformando funcionalidades em experiências que fazem sentido.",
    photo: "/team/ana.jpg",
    linkedin: "https://www.linkedin.com/in/ana-furlaneto-a47746368/",
    github: "https://github.com/acfurlaneto",
  },
  {
    id: "giovana-dangelo",
    name: "Giovana D'Angelo",
    contribution: "Hardware e IoT",
    description: "Conectando o mundo físico à inteligência do FieldNode.",
    photo: "/team/giovana.jpg",
    linkedin: "https://www.linkedin.com/in/giovanamdangelo/",
  },
  {
    id: "paola-soares-machado",
    name: "Paola Soares Machado",
    contribution: "Full Stack e decisões",
    description: "Integrando tecnologia, produto e decisões em uma única solução.",
    photo: "/team/paola.jpg",
    linkedin: "https://www.linkedin.com/in/paolasoaresmachado/",
    github: "https://github.com/Paola5858",
  },
] as const;

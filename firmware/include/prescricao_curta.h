#pragma once

namespace fieldnode::prescricao_curta {

struct Entry {
  const char* code;
  const char* text;
};

// Tabela fixa, revisada junto do contrato/playbook. Nao e texto gerado por LLM.
constexpr Entry P03{"P03", "TEMP ALTA: PARAR E INSPECIONAR"};

inline const char* text_for(const char* code) {
  if (code != nullptr && code[0] == 'P' && code[1] == '0' && code[2] == '3' && code[3] == '\0') {
    return P03.text;
  }
  return nullptr;
}

}  // namespace fieldnode::prescricao_curta

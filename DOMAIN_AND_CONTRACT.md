# Domínio e Contrato do Sistema

## 1. Domínio

**Domínio:** Monitoramento da biodiversidade e dados de observações de biodiversidade.

**Família de dados:** Registros de observações de espécies animais e vegetais, contendo informações taxonômicas, temporais, espaciais e contextuais.

O sistema tem como foco transformar conjuntos de dados heterogêneos de observações de biodiversidade em uma representação estruturada e interoperável baseada no padrão **Darwin Core**.

---

## 2. Problema Apoiado

O sistema apoia a análise e transformação de conjuntos de dados de observações de biodiversidade que podem apresentar diferentes nomes de campos, formatos e formas de representação.

O principal problema abordado é a falta de padronização entre diferentes conjuntos de dados de biodiversidade, dificultando:

- a interpretação dos campos;
- a identificação do significado das variáveis;
- a normalização dos valores;
- a transformação dos registros para uma representação comum;
- a avaliação da qualidade dos dados;
- a produção de dados interoperáveis.

---

## 3. Decisão Apoiada

O sistema apoia a seguinte decisão:

> **Determinar se um conjunto de dados de observações de biodiversidade pode ser interpretado, transformado e representado de acordo com o contrato definido para Darwin Core, identificando as transformações e validações necessárias.**

A decisão do sistema é restrita à **interpretação, transformação e avaliação da qualidade dos dados**.

O sistema não realiza decisões ecológicas, ambientais ou de conservação sobre as espécies observadas.

---

## 4. Usuário do Resultado

O sistema é destinado a usuários que trabalham com dados de biodiversidade, como:

- cientistas de dados;
- engenheiros de dados;
- pesquisadores em biodiversidade;
- pesquisadores em ecologia;
- gestores de dados de biodiversidade;
- desenvolvedores de sistemas de informação sobre biodiversidade.

O usuário deve ser capaz de fornecer um conjunto de dados e uma instrução geral de análise.

---

## 5. Dados de Entrada

### 5.1 Formato

A implementação atual aceita:

```text
CSV

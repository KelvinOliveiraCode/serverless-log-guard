# Retenção e proteção de dados

Retenção guarda, proteção apaga — e as duas precisam existir no mesmo desenho.
Guardar tudo para sempre não é prudente, é preguiça com custo de disco e custo
jurídico. Apagar cedo demais destrói prova. A política deste laboratório
resolve a tensão com duas regras simples.

## O que fica, e por quanto tempo

| Nível | Dias | Por quê |
|---|---|---|
| debug | 7 | Ruído operacional. Passou uma semana sem ninguém olhar, ninguém vai olhar. |
| info | 30 | Um mês cobre o ciclo de fechamento e a pergunta "o que mudou". |
| erro | 90 | Um trimestre cobre investigação, post-mortem e reincidência. |
| auditoria | 365, nunca descartada | Prova. Prova descartada por rotina é prova destruída. |

Os números não são mágicos; são os da especificação, e qualquer mudança deve
vir com o motivo escrito. "O time ignorava o relatório" é motivo. "Quero
menos linha" não é.

## Mascarar antes de reter

A ordem do pipeline é lei aqui: normalizar, detectar PII, mascarar, e só
então decidir retenção. Se a retenção viesse antes do mascaramento, o
conteúdo guardado teria dado sensível, e apagar depois não apaga o que já foi
escrito no disco. O que fica retido já está limpo; o que foi descartado nunca
existiu com PII.

Isso conecta retenção com proteção de dados sem citar serviço específico:
dado que não existe não vaza, não é pedido em auditoria e não custa
armazenamento. A forma mais barata de proteger um dado é não tê-lo.

## O que este laboratório não resolve

Retenção decide, não apaga. O `deve_manter` responde sim ou não; o descarte
real seria outro sistema, com confirmação, trilha e reversão. Um pipeline que
apagasse de verdade precisaria de muito mais: janela de arrependimento,
cópia de segurança antes do corte, e alguém responsável assinando.

Também não há consentimento aqui. Evento sintético não tem titular, e por
isso não há pedido de exclusão, portabilidade ou oposição. Num sistema real,
cada um desses direitos furaria a tabela de prazos — e a tabela teria uma
coluna a mais: "exceto quando o titular pedir".

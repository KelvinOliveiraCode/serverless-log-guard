# Modelo de custo serverless: execução, duração e memória

Em serverless, a conta chega por três grandezas que se multiplicam: quantas vezes o código foi chamado, por quanto tempo cada chamada durou e quanto recurso foi reservado. Este documento descreve o modelo a partir dos campos `id`, `tipo` e `nivel` dos eventos do SluGuard.

## 1. O que compõe o custo

O custo total é a soma do custo de todas as execuções. Para uma única execução, o custo é o produto de três fatores: o preço por unidade de tempo de processamento, o tempo de duração efetivo e o multiplicador definido pela memória alocada.

A fórmula, escrita por extenso, é:

**custo de execução igual ao custo por unidade de tempo de processamento vezes o tempo de duração da execução vezes o multiplicador de memória alocada.**

O preço mede o tempo decorrido — da chegada do evento até o fim do código — convertido em fração de segundo (geralmente milissegundos) e multiplicado pela memória configurada. Mais memória sobe o preço por milissegundo, mas traz mais processamento.

Um exemplo: `monitor` com `nivel` `debug` chega centenas de vezes por minuto e é resolvido em poucos milissegundos; custo unitário ínfimo, mas o volume importa. Já `pagamento` com `nivel` `erro` pode acionar fluxo de recomposição mais longo — consultas externas, recriação de contexto — durando vários segundos, custando muito mais por execução.

O número de execuções, isolado, não revela o custo.

## 2. Por que a duração domina e o número de execuções engana

A métrica mais visível é o número de execuções. É natural concluir que o custo cresce linearmente: o dobro de execuções, mantida a duração média, quase dobra a conta. Mas isso é enganoso porque ignora a dispersão enorme da duração entre tipos de evento.

Pelo campo `tipo`, a variação de duração atinge três ou quatro ordens de grandeza: `login` com `nivel` `info` em alguns milissegundos; `pedido` com `nivel` `erro` em vários segundos; `auditoria` com buscas em registros históricos, tanto quanto um `pagamento` complexo.

Isso significa que a grande maioria das execuções pode representar menos de 1 % do tempo total, enquanto os poucos casos mais complexos consomem a maior parte dos segundos. Otimizar apenas o número de execuções gasta esforço em um termo já pequeno e deixa intacta a raiz do custo: os segundos dos casos pesados.

A análise correta inverte a pergunta. Em vez de "quantas vezes foi chamado?", pergunta-se "quantos segundos foram consumidos por tipo". Agrupando os `Evento` por `tipo` e somando as durações, fica claro qual caminho de evento é verdadeiramente caro.

## 3. Memória como multiplicador silencioso

A memória é tratada como configuração isolada do código, mas ela determina o preço por milissegundo. Reservar mais memória aumenta proporcionalmente o custo unitário de tempo, na mesma razão — o que, em tese, preserva o custo por segundo bruto.

Esse equilíbrio aparente esconde, porém, um comportamento que distorce a conta: com mais memória, o poder de processamento é escalado, o que tende a reduzir a duração da execução. Se o ganho de velocidade for maior que o aumento de preço por milissegundo, o custo total cai; se for menor, sobe. A relação não é linear e depende do workload.

Considere os tipos de evento do SluGuard. Um evento `monitor` em `nivel` `debug` lê um JSON pequeno e termina; dobrar a memória quase não reduz seu milissegundo de duração, então o custo sobe proporcionalmente — desperdício silencioso. Já um evento `auditoria` com `campos` extensos, que executa varredura de dados pessoais, beneficia-se de memória maior, pois o trabalho é intensivo e a duração cai de forma relevante.

O efeito é "silencioso": a mudança altera o preço unitário instantaneamente, mas o impacto no total só aparece quando as durações se ajustam e o volume se estabiliza.

Meça o custo total, não o preço por unidade; teste elevação de memória observando a duração média por `tipo`. O ganho só é real quando a redução de segundos compensa o multiplicador de memória.

## 4. O que o modelo não captura: cold start, transferência, armazenamento

O modelo de três fatores descreve o custo de execução do código, mas não é a conta final. Três classes de custo ficam de fora.

**Cold start.** O modelo cobra apenas pelo tempo de processamento. Quando a função não é chamada há algum tempo, a plataforma alocará um novo ambiente e carregará o código, adicionando um tempo sem trabalho útil. Esse tempo é cobrado como duração, mas o efeito colateral é o atraso percebido pelo usuário. Para eventos críticos como `login` ou `pagamento`, o cold start pode gerar retentativas automáticas, e cada retentativa é mais uma execução cobrada. Em cargas com picos esparsos, os cold starts representam fração significativa do tempo total.

**Transferência de dados.** Nenhum dos três fatores conta o movimento de bytes. Eventos grandes chegam com `campos` extensos, que a normalização lê. Transferir dados entre regiões ou receber payloads de `monitor` tem custo próprio, linear com os bytes e independente do número de execuções. Um evento `auditoria` com megabytes de `campos` vira um trabalho de transferência caro.

**Armazenamento.** O modelo não inclui disco e backups. Log de auditoria, eventos `erro` retidos e reprocessamento ocupam armazenamento contínuo, cobrado por gigabyte por mês e independente do número de execuções. Em fluxos de auditoria, a retenção regulatória pode fazer o armazenamento dominar o custo de execução.

## Conclusão

O núcleo é a multiplicação de execuções por duração por memória, mas a conta final depende de fatores que a fórmula não expressa: agrupe os `Evento` por `tipo`, meça a duração, teste variações de memória pelo custo total e some transferência e armazenamento.

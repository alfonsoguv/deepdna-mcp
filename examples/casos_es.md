# Casos docentes de farmacogenética con DeepDNA

Ocho casos para un curso de farmacogenética. Cada uno plantea una pregunta sobre lo que dice una guía (CPIC o DPWG) para un grupo de fenotipo o de genotipo; dos de ellos enseñan qué se responde cuando no hay recomendación de guía (caso 7) o no hay registro (caso 8). Cada caso da la llamada exacta con la que se consulta, recoge lo que devuelve DeepDNA con su fuente y termina con una pregunta para discutir en clase.

> **Aviso.** Material educativo. No es consejo médico y no sustituye a la ficha técnica del medicamento ni al criterio clínico. Los casos preguntan por grupos genéricos de fenotipo o de genotipo («metabolizadores lentos», «genotipo 677TT»), no por personas: las llamadas solo llevan el símbolo de un gen y el nombre de un fármaco, nunca un genotipo. Los registros cambian cuando se actualizan las guías: las respuestas de esta hoja son las que devolvía la API el **15 de noviembre de 2026** (campo `data_as_of`: `2026-11-08T12:09:46.225Z`). Antes de usarla en clase, repita las llamadas y compare.

## Cómo leer una respuesta

Cada caso se puede consultar de dos maneras, que devuelven el mismo registro:

- **API REST**, con `curl`: `https://deepdna.ai/api/v1/pgx/{gen}/{fármaco}`. Documentación: <https://deepdna.ai/docs/>.
- **Servidor MCP** `https://deepdna.ai/mcp`, herramienta `lookup_drug_gene`, desde un asistente conectado (<https://deepdna.ai/connect/>) o con una petición JSON-RPC como la del cuaderno [pgx_lookup.ipynb](pgx_lookup.ipynb).

El nombre del fármaco va en inglés y como nombre genérico (`capecitabine`, no «capecitabina»).

Campos del registro:

| Campo | Qué es |
|---|---|
| `guideline` | En qué se apoya el registro: `CPIC`, `DPWG`, `drug label` (ficha del medicamento), una combinación (`DPWG; FDA label`, `CPIC; FDA label`) cuando el registro recoge una guía y una ficha, o `null` cuando se apoya en la literatura primaria |
| `level` | El nivel que CPIC asigna al par gen–fármaco, copiado de la base de datos de CPIC. Califica el par, no la fuerza de una recomendación concreta. «(provisional)» marca un par que CPIC todavía no ha cubierto en una guía. Es `null` cuando CPIC no ha calificado el par. La escala se explica en la [documentación](https://deepdna.ai/docs/#pgx) |
| `summary` | Lo que recomienda la fuente, por grupo de fenotipo |
| `phenotypes` | Los grupos de fenotipo (o de genotipo) que cubre el registro |
| `sources` | Las fuentes, cada una con su enlace. En «Fuente» cada caso enlaza las principales y dice qué más cita el registro |

En cada caso, el campo `summary` se copia en inglés tal como lo devuelve la API y se acompaña de una traducción. Si hay alguna diferencia, vale el original. Equivalencias usadas: *poor metabolizer*, metabolizador lento; *intermediate*, intermedio; *normal*, normal; *rapid*, rápido; *ultra-rapid*, ultrarrápido.

---

## Caso 1. CYP2C19 y clopidogrel (CPIC)

**Pregunta.** Un clínico quiere saber qué dice la guía sobre el clopidogrel en metabolizadores lentos de CYP2C19.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/CYP2C19/clopidogrel
```

MCP: `lookup_drug_gene` con `{"gene": "CYP2C19", "drug": "clopidogrel"}`.

**Respuesta.** `guideline`: `CPIC` · `level`: `CPIC A`

> Prodrug activated by CYP2C19. CPIC 2022 recommends an alternative antiplatelet (prasugrel or ticagrelor) for poor and intermediate metabolizers undergoing PCI for acute coronary syndromes. FDA boxed warning about reduced effectiveness in poor metabolizers.

Traducción: profármaco que CYP2C19 activa. CPIC 2022 recomienda un antiagregante alternativo (prasugrel o ticagrelor) en los metabolizadores lentos e intermedios sometidos a intervención coronaria percutánea (ICP) por síndrome coronario agudo. Advertencia destacada (*boxed warning*) de la FDA sobre la menor eficacia en metabolizadores lentos.

**Fuente.** [Lee et al., Clin Pharmacol Ther 2022 (CPIC clopidogrel guideline update)](https://pubmed.ncbi.nlm.nih.gov/35034351/). El registro cita además la ficha de la FDA y las páginas del gen en CPIC, PharmGKB y PharmVar.

**Para discutir.** El resumen limita la recomendación a un contexto clínico concreto (ICP por síndrome coronario agudo). ¿Qué se puede afirmar, citando solo este registro, sobre el clopidogrel en otras indicaciones? ¿Dónde habría que mirar?

---

## Caso 2. CYP2D6 y risperidona (DPWG)

**Pregunta.** Una farmacéutica de hospital quiere saber qué dice la guía sobre la risperidona en metabolizadores lentos y ultrarrápidos de CYP2D6.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/CYP2D6/risperidone
```

MCP: `lookup_drug_gene` con `{"gene": "CYP2D6", "drug": "risperidone"}`.

**Respuesta.** `guideline`: `DPWG` · `level`: `CPIC B (provisional)`

> Antipsychotic converted by CYP2D6 to 9-hydroxyrisperidone, which is also active. DPWG recommends a lower dose for poor metabolizers and an alternative drug or dose titration for ultra-rapid metabolizers.

Traducción: antipsicótico que CYP2D6 convierte en 9-hidroxirrisperidona, que también es activa. DPWG recomienda una dosis menor en los metabolizadores lentos y, en los ultrarrápidos, un fármaco alternativo o un ajuste gradual de la dosis (*dose titration*).

**Fuente.** [Beunk et al., Eur J Hum Genet 2024 (DPWG guideline: CYP2D6, CYP3A4, CYP1A2 and antipsychotics)](https://pubmed.ncbi.nlm.nih.gov/37002327/). El registro cita además la ficha de la FDA de la risperidona (DailyMed), las páginas del gen en CPIC, PharmVar y PharmGKB y el consenso de CPIC y DPWG sobre la traducción de genotipo a fenotipo de CYP2D6 (Caudle et al., Clin Transl Sci 2020).

**Para discutir.** El registro se apoya en DPWG, pero el campo `level` dice `CPIC B (provisional)`. ¿Qué informa cada campo y por qué no se contradicen? El resumen dice «una dosis menor» sin dar una cifra: ¿dónde debe buscarse, y por qué un asistente no debería completarla por su cuenta?

---

## Caso 3. CYP2D6 y aripiprazol (DPWG)

**Pregunta.** El mismo servicio pregunta ahora por el aripiprazol en metabolizadores lentos de CYP2D6.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/CYP2D6/aripiprazole
```

MCP: `lookup_drug_gene` con `{"gene": "CYP2D6", "drug": "aripiprazole"}`.

**Respuesta.** `guideline`: `DPWG` · `level`: `CPIC B (provisional)`

> Antipsychotic metabolized by CYP2D6. DPWG recommends a lower dose for poor metabolizers and no adjustment for other CYP2D6 phenotypes.

Traducción: antipsicótico metabolizado por CYP2D6. DPWG recomienda una dosis menor en los metabolizadores lentos y ningún ajuste en los demás fenotipos de CYP2D6.

**Fuente.** [Beunk et al., Eur J Hum Genet 2024 (DPWG guideline: CYP2D6, CYP3A4, CYP1A2 and antipsychotics)](https://pubmed.ncbi.nlm.nih.gov/37002327/). El registro cita además las páginas del gen en CPIC, PharmVar y PharmGKB y el consenso de CPIC y DPWG sobre la traducción de genotipo a fenotipo de CYP2D6 (Caudle et al., Clin Transl Sci 2020).

**Para discutir.** Mismo gen, misma guía y mismo grupo terapéutico que en el caso 2, pero la recomendación para los metabolizadores ultrarrápidos es distinta. ¿Qué dato del resumen de la risperidona ayuda a plantear una hipótesis, y cómo la comprobaría en la guía antes de darla por buena? ¿Qué enseña esto sobre extrapolar de un fármaco a otro de la misma clase?

---

## Caso 4. UGT1A1 e irinotecán (DPWG y ficha de la FDA)

**Pregunta.** Un oncólogo quiere saber qué dice la guía sobre el irinotecán en metabolizadores lentos de UGT1A1.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/UGT1A1/irinotecan
```

MCP: `lookup_drug_gene` con `{"gene": "UGT1A1", "drug": "irinotecan"}`.

**Respuesta.** `guideline`: `DPWG; FDA label` · `level`: `CPIC A (provisional)`

> Active metabolite SN-38 is cleared by UGT1A1. The FDA label notes a higher risk of severe neutropenia with \*28/\*28, \*6/\*6 or \*6/\*28 and advises considering a starting dose reduced by at least one level. DPWG recommends 70% of the standard starting dose for poor metabolizers (two decreased-function alleles such as \*6, \*28 or \*37), to lower the risk of severe neutropenia or diarrhea, and no reduction for intermediate metabolizers.

Traducción: el metabolito activo SN-38 se elimina por UGT1A1. La ficha de la FDA señala un mayor riesgo de neutropenia grave con \*28/\*28, \*6/\*6 o \*6/\*28 y aconseja valorar una dosis inicial reducida en al menos un nivel. DPWG recomienda el 70 % de la dosis inicial estándar en los metabolizadores lentos (dos alelos de función disminuida, como \*6, \*28 o \*37), para reducir el riesgo de neutropenia grave o de diarrea, y ninguna reducción en los metabolizadores intermedios.

**Fuente.** [Hulshof et al., Eur J Hum Genet 2023 (DPWG UGT1A1–irinotecan guideline; correction PMID 36797469)](https://pubmed.ncbi.nlm.nih.gov/36443464/) y [Camptosar (irinotecan) prescribing information, FDA/DailyMed (sections 2.3 and 5.3, reduced UGT1A1 activity)](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e518dfc6-7e93-4fee-a66c-51e1ab71c056). El registro cita además las páginas del gen en CPIC, PharmGKB y MedlinePlus.

**Para discutir.** El registro recoge dos fuentes que expresan la reducción de forma distinta: la ficha de la FDA habla de «al menos un nivel» de dosis y DPWG del 70 % de la dosis inicial estándar. ¿Cómo se presentan las dos sin fundirlas en una sola frase? La ficha citada es la estadounidense: ¿qué dice la ficha técnica autorizada en España?

---

## Caso 5. DPYD y capecitabina (CPIC)

**Pregunta.** Una oncóloga quiere saber qué dice la guía sobre la capecitabina en metabolizadores intermedios y lentos de DPYD.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/DPYD/capecitabine
```

MCP: `lookup_drug_gene` con `{"gene": "DPYD", "drug": "capecitabine"}`.

**Respuesta.** `guideline`: `CPIC` · `level`: `CPIC A`

> Oral prodrug converted in the body to fluorouracil, which DPD, encoded by DPYD, breaks down. CPIC (Amstutz et al. 2018, with its current recommendation table) recommends avoiding fluorouracil and its prodrugs in DPYD poor metabolizers (activity score 0 or 0.5; strong); at activity score 0.5, if no alternative is considered suitable, a strongly reduced dose with early therapeutic drug monitoring. For intermediate metabolizers it recommends a 50% lower starting dose, then titration on toxicity or drug levels, increasing the dose if the first two cycles are well tolerated (activity score 1 strong, 1.5 moderate); people with two copies of c.2846A>T may need more than a 50% reduction. Normal metabolizers: label-recommended dosing (strong). A consumer raw file or a limited variant panel with no variant found does not establish normal-metabolizer status: these recommendations apply to a phenotype from a validated clinical DPYD test, or DPD phenotyping, ordered by the prescriber.

Traducción: profármaco oral que el organismo convierte en fluorouracilo, al que degrada la DPD, codificada por DPYD. CPIC (Amstutz et al. 2018, con su tabla de recomendaciones vigente) recomienda evitar el fluorouracilo y sus profármacos en los metabolizadores lentos de DPYD (puntuación de actividad 0 o 0,5; recomendación fuerte); con puntuación de actividad 0,5, si ninguna alternativa se considera adecuada, una dosis muy reducida con monitorización terapéutica temprana del fármaco. En los metabolizadores intermedios recomienda una dosis inicial un 50 % menor y, después, ajustarla según la toxicidad o los niveles del fármaco, aumentándola si los dos primeros ciclos se toleran bien (puntuación de actividad 1, fuerte; 1,5, moderada); las personas con dos copias de c.2846A>T pueden necesitar una reducción superior al 50 %. Metabolizadores normales: la dosis que recomienda la ficha del medicamento (fuerte). Un fichero bruto de un test de consumo, o un panel limitado de variantes, en el que no aparece ninguna variante no establece la condición de metabolizador normal: estas recomendaciones se aplican a un fenotipo obtenido con una prueba clínica validada de DPYD, o con un fenotipado de DPD, solicitados por el prescriptor.

**Fuente.** [Amstutz et al., Clin Pharmacol Ther 2018 (CPIC DPYD and fluoropyrimidine guideline: 2017 update)](https://pubmed.ncbi.nlm.nih.gov/29152729/). El registro cita además las páginas del gen en CPIC y PharmGKB.

**Para discutir.** Este registro se apoya solo en CPIC. Busque si DPWG tiene una guía para este par y qué indica la ficha técnica española sobre la determinación de DPD antes del tratamiento, y compare. La última frase del resumen distingue entre «no se encontró ninguna variante» y «metabolizador normal»: ¿por qué no son lo mismo?

---

## Caso 6. CYP2D6 y codeína (CPIC)

**Pregunta.** Una médica de familia quiere saber qué dice la guía sobre la codeína en metabolizadores ultrarrápidos de CYP2D6.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/CYP2D6/codeine
```

MCP: `lookup_drug_gene` con `{"gene": "CYP2D6", "drug": "codeine"}`.

**Respuesta.** `guideline`: `CPIC` · `level`: `CPIC A`

> Prodrug converted to morphine by CYP2D6. CPIC recommends avoiding codeine in poor metabolizers (diminished analgesia) and in ultra-rapid metabolizers (risk of serious toxicity). The FDA label carries a boxed warning on ultra-rapid metabolism and life-threatening respiratory depression in children, contraindicates codeine under 12 years, and states that breastfeeding is not recommended during treatment.

Traducción: profármaco que CYP2D6 convierte en morfina. CPIC recomienda evitar la codeína en los metabolizadores lentos (analgesia disminuida) y en los ultrarrápidos (riesgo de toxicidad grave). La ficha de la FDA incluye una advertencia destacada (*boxed warning*) sobre el metabolismo ultrarrápido y la depresión respiratoria potencialmente mortal en niños, contraindica la codeína en menores de 12 años e indica que no se recomienda la lactancia durante el tratamiento.

**Fuente.** [Crews et al., Clin Pharmacol Ther 2021 (CPIC guideline: CYP2D6, OPRM1, COMT and opioids)](https://pubmed.ncbi.nlm.nih.gov/33387367/) y [FDA label, codeine sulfate tablets (DailyMed: boxed warning, contraindications, lactation)](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=010905f9-3bcb-4b50-9fe8-a3ad0010f14c), la ficha de la FDA de la codeína, de la que proceden las tres afirmaciones de la última frase del resumen. El registro cita además las páginas del gen en CPIC, PharmGKB y PharmVar y el consenso de CPIC y DPWG sobre la traducción de genotipo a fenotipo de CYP2D6 (Caudle et al., Clin Transl Sci 2020).

**Para discutir.** La guía recomienda lo mismo (evitar la codeína) para dos fenotipos opuestos. Explique el mecanismo en cada caso a partir de la primera frase del resumen. ¿Qué otros fármacos del registro de CYP2D6 son profármacos? (Pista: `curl -s https://deepdna.ai/api/v1/pgx/CYP2D6` los lista todos.)

---

## Caso 7. MTHFR y metotrexato (sin recomendación de guía)

**Pregunta.** Un reumatólogo quiere saber qué dice la guía sobre el metotrexato en personas con el genotipo 677TT de MTHFR.

**Llamada.**

```bash
curl -s https://deepdna.ai/api/v1/pgx/MTHFR/methotrexate
```

MCP: `lookup_drug_gene` con `{"gene": "MTHFR", "drug": "methotrexate"}`.

**Respuesta.** `guideline`: `null` · `level`: `CPIC C (provisional)`

> Methotrexate is a folate antagonist, and MTHFR variants have been studied as a factor in its side effects. One cross-sectional study of 214 rheumatoid arthritis patients found 677TT associated with central-nervous-system side effects of methotrexate (Weisman et al., Arthritis Rheum 2006). A DPWG guideline found insufficient evidence for an MTHFR–methotrexate gene–drug interaction (van der Pol et al., Eur J Hum Genet 2024).

Traducción: el metotrexato es un antagonista del folato, y las variantes de MTHFR se han estudiado como factor en sus efectos adversos. Un estudio transversal de 214 pacientes con artritis reumatoide encontró que 677TT se asociaba a efectos adversos del metotrexato en el sistema nervioso central (Weisman et al., Arthritis Rheum 2006). Una guía de DPWG encontró pruebas insuficientes de una interacción gen–fármaco entre MTHFR y metotrexato (van der Pol et al., Eur J Hum Genet 2024).

**Fuente.** [van der Pol et al., Eur J Hum Genet 2024 (DPWG guideline: ABCG2/HLA-B and allopurinol, MTHFR and folic acid/methotrexate)](https://pubmed.ncbi.nlm.nih.gov/36056234/) y [Weisman et al., Arthritis Rheum 2006 (folate-pathway risk genotypes, incl. MTHFR 677TT, and methotrexate side effects in rheumatoid arthritis)](https://pubmed.ncbi.nlm.nih.gov/16447238/). El registro cita además dos estudios sobre la actividad enzimática de las variantes de MTHFR (Frosst et al., Nat Genet 1995; Weisberg et al., Mol Genet Metab 1998).

**Para discutir.** Aquí hay registro, pero `guideline` es `null`: lo que se recoge es un hallazgo de un estudio y la conclusión de una guía de que las pruebas son insuficientes. ¿En qué se diferencia responder «la guía no encontró pruebas suficientes» de responder «no hay nada»? ¿Cómo se lo explicaría a quien llega con un resultado de MTHFR y espera un cambio de tratamiento?

---

## Caso 8. VKORC1 y acenocumarol (no hay registro)

**Pregunta.** Una médica quiere saber qué dice la guía sobre el acenocumarol en portadores de variantes de VKORC1.

**Llamada.**

```bash
curl -s -w '\nHTTP %{http_code}\n' https://deepdna.ai/api/v1/pgx/VKORC1/acenocoumarol
```

MCP: `lookup_drug_gene` con `{"gene": "VKORC1", "drug": "acenocoumarol"}`.

**Respuesta.** HTTP `404`. No hay registro. El cuerpo lleva un objeto `error` y el bloque `meta` habitual (aquí con sangría para leerlo; `curl` lo devuelve en una sola línea):

```json
{
  "error": {
    "code": "not_found",
    "resource": "pgx",
    "id": "VKORC1/acenocoumarol",
    "hint": "Drugs curated for VKORC1: warfarin"
  },
  "meta": {
    "disclaimer": "Educational information only, not medical advice or diagnosis. Consult a clinician before acting on genetic information.",
    "api_version": "2026-09-20",
    "docs": "https://deepdna.ai/docs/",
    "status": "live",
    "data_as_of": "2026-11-08T12:09:46.225Z",
    "freshness": "https://deepdna.ai/api/v1/freshness"
  }
}
```

Por MCP, la herramienta devuelve un resultado con `isError: true` y este texto:

> No guidance curated for VKORC1 and "acenocoumarol". Curated drugs: warfarin.

Traducción: no hay orientación revisada para VKORC1 y «acenocoumarol». Fármacos con registro: warfarina.

**Fuente.** Ninguna: sin registro no hay nada que citar. La respuesta correcta es «DeepDNA no tiene registro para este par».

**Para discutir.** La pista (`hint`) dice que para VKORC1 sí hay registro de la warfarina. ¿Es legítimo responder con el registro de la warfarina porque ambos son antagonistas de la vitamina K? ¿Qué significa, y qué no significa, que un par no esté en una base de datos curada? Busque directamente en CPIC y en DPWG si existe una guía para este par y con qué fecha.

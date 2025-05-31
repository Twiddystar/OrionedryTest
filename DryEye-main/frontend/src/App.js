import React, { useState } from 'react';
import './App.css';

function App() {
  const [currentSection, setCurrentSection] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [result, setResult] = useState(null);

  const sections = [
    {
      title: "Sintomi Principali",
      description: "Valuta quanto spesso hai questi sintomi (da 0 = mai a 4 = sempre)",
      questions: [
        { id: 1, text: "I tuoi occhi ti sembrano secchi o irritati?", type: "scale" },
        { id: 2, text: "Senti bruciore o pizzicore agli occhi?", type: "scale" },
        { id: 3, text: "Hai sensazione di sabbia o corpo estraneo?", type: "scale" },
        { id: 4, text: "Avverti fastidio alla luce (fotofobia)?", type: "scale" },
        { id: 5, text: "La tua vista diventa offuscata nel corso della giornata?", type: "scale" },
        { id: 6, text: "I tuoi occhi lacrimano spontaneamente?", type: "scale" },
        { id: 7, text: "I sintomi peggiorano alla sera o dopo uso del computer?", type: "scale" }
      ]
    },
    {
      title: "Fattori Predisponenti",
      description: "Rispondi Sì o No alle seguenti domande",
      questions: [
        { id: 8, text: "Usi frequentemente schermi (PC, tablet, smartphone)?", type: "yesno" },
        { id: 9, text: "Indossi lenti a contatto?", type: "yesno" },
        { id: 10, text: "Hai mai fatto un intervento agli occhi?", type: "yesno" },
        { id: 11, text: "Hai una malattia autoimmune diagnosticata (es. Sjögren, lupus)?", type: "yesno" },
        { id: 12, text: "Assumi farmaci per la pressione, depressione o antistaminici?", type: "yesno" }
      ]
    },
    {
      title: "Risposte ai Trattamenti",
      description: "Indica se hai notato miglioramenti con questi trattamenti",
      questions: [
        { id: 13, text: "Noti miglioramento con lacrime artificiali?", type: "yesno" },
        { id: 14, text: "Noti miglioramento dopo impacchi caldi?", type: "yesno" },
        { id: 15, text: "I sintomi compaiono soprattutto al risveglio?", type: "yesno" },
        { id: 16, text: "Hai provato lacrime più viscose o gel, con miglioramento?", type: "yesno" }
      ]
    },
    {
      title: "Diagnostica Riferita",
      description: "Indica se conosci questi aspetti della tua condizione",
      questions: [
        { id: 17, text: "Ti hanno mai detto che hai un film lacrimale instabile?", type: "yesno" },
        { id: 18, text: "Ti hanno mai fatto il test di Schirmer (carta sotto la palpebra)?", type: "yesno" },
        { id: 19, text: "Sai se le tue ghiandole di Meibomio funzionano bene (MGD)?", type: "yesno" },
        { id: 20, text: "I tuoi sintomi sono molto forti anche se all'esame l'occhio è 'normale'?", type: "yesno" }
      ]
    }
  ];

  const scaleLabels = ["Mai", "Raramente", "A volte", "Spesso", "Sempre"];

  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const nextSection = () => {
    if (currentSection < sections.length - 1) {
      setCurrentSection(currentSection + 1);
    } else {
      calculateResult();
    }
  };

  const prevSection = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
    }
  };

  const calculateResult = () => {
    // Algoritmo di classificazione dell'occhio secco
    const evaporativeQuestions = [2, 3, 5, 7, 14, 19];
    const aqueousDeficitQuestions = [1, 6, 15, 16, 11, 18];
    const neuropathicIndicator = answers[20] === 'si';
    
    let evaporativeScore = 0;
    let aqueousScore = 0;
    let totalSymptoms = 0;

    // Calcola punteggio evaporativo
    evaporativeQuestions.forEach(q => {
      if (q <= 7) {
        // Domande scala 0-4
        evaporativeScore += parseInt(answers[q] || 0);
      } else {
        // Domande sì/no (sì = 2 punti, no = 0)
        evaporativeScore += answers[q] === 'si' ? 2 : 0;
      }
    });

    // Calcola punteggio deficit acquoso
    aqueousDeficitQuestions.forEach(q => {
      if (q <= 7) {
        // Domande scala 0-4
        aqueousScore += parseInt(answers[q] || 0);
      } else {
        // Domande sì/no (sì = 2 punti, no = 0)
        aqueousScore += answers[q] === 'si' ? 2 : 0;
      }
    });

    // Calcola sintomi totali (domande 1-7)
    for (let i = 1; i <= 7; i++) {
      totalSymptoms += parseInt(answers[i] || 0);
    }

    // Logica di classificazione
    let type, description, recommendations;

    if (neuropathicIndicator && totalSymptoms >= 15) {
      type = "Occhio Secco Neuropatico";
      description = "Il tuo profilo è compatibile con un occhio secco di tipo neuropatico. I sintomi sono intensi ma spesso l'esame oculistico può risultare normale o con pochi segni clinici visibili.";
      recommendations = [
        "Considera una valutazione neurologica specializzata",
        "Potrebbero essere utili terapie specifiche per il dolore neuropatico",
        "Mantieni un diario dei sintomi per identificare i trigger"
      ];
    } else if (evaporativeScore >= 12 && aqueousScore >= 10) {
      type = "Occhio Secco Misto";
      description = "Il tuo profilo presenta caratteristiche sia dell'occhio secco evaporativo che del deficit acquoso. Questa forma combinata richiede un approccio terapeutico multiplo.";
      recommendations = [
        "Combina impacchi caldi e lacrime artificiali",
        "Valuta igiene palpebrale quotidiana",
        "Potrebbero essere necessari diversi tipi di lacrime artificiali"
      ];
    } else if (evaporativeScore > aqueousScore && evaporativeScore >= 8) {
      type = "Occhio Secco Evaporativo";
      description = "Il tuo profilo è compatibile con un occhio secco di tipo evaporativo, spesso legato alla disfunzione delle ghiandole di Meibomio che producono la componente oleosa delle lacrime.";
      recommendations = [
        "Impacchi caldi sulle palpebre 2 volte al giorno",
        "Massaggio delicato delle palpebre",
        "Igiene palpebrale con prodotti specifici",
        "Riduci l'uso prolungato di schermi digitali"
      ];
    } else if (aqueousScore >= 8) {
      type = "Occhio Secco da Deficit Acquoso";
      description = "Il tuo profilo è compatibile con un occhio secco da deficit acquoso, caratterizzato da una ridotta produzione della componente acquosa delle lacrime.";
      recommendations = [
        "Lacrime artificiali frequenti (senza conservanti se usate spesso)",
        "Considera lacrime più viscose per la notte",
        "Evita ambienti secchi o ventosi",
        "Valuta possibili farmaci che potrebbero influire sulla produzione lacrimale"
      ];
    } else {
      type = "Occhio Secco Lieve";
      description = "I tuoi sintomi suggeriscono una forma lieve di occhio secco. Potrebbero essere sufficienti misure preventive e trattamenti semplici.";
      recommendations = [
        "Lacrime artificiali al bisogno",
        "Pause frequenti durante l'uso di schermi",
        "Mantieni una buona idratazione",
        "Controlla l'umidità degli ambienti dove passi più tempo"
      ];
    }

    setResult({ type, description, recommendations, scores: { evaporativeScore, aqueousScore, totalSymptoms } });
    setShowResults(true);
  };

  const exportToPDF = () => {
    const printContent = `
      QUESTIONARIO OCCHIO SECCO - RISULTATO
      
      Data: ${new Date().toLocaleDateString('it-IT')}
      
      CLASSIFICAZIONE: ${result.type}
      
      DESCRIZIONE:
      ${result.description}
      
      RACCOMANDAZIONI:
      ${result.recommendations.map((rec, index) => `${index + 1}. ${rec}`).join('\n')}
      
      PUNTEGGI:
      - Evaporativo: ${result.scores.evaporativeScore}
      - Deficit Acquoso: ${result.scores.aqueousScore}
      - Sintomi Totali: ${result.scores.totalSymptoms}
      
      DISCLAIMER:
      Questo risultato non sostituisce una valutazione medica professionale. 
      Porta con te questo risultato alla visita oculistica per una valutazione completa.
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Risultato Questionario Occhio Secco</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
            .disclaimer { background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; margin-top: 20px; border-radius: 5px; }
          </style>
        </head>
        <body>
          <h1>QUESTIONARIO OCCHIO SECCO - RISULTATO</h1>
          <p><strong>Data:</strong> ${new Date().toLocaleDateString('it-IT')}</p>
          <p><strong>CLASSIFICAZIONE:</strong> ${result.type}</p>
          <h2>DESCRIZIONE:</h2>
          <p>${result.description}</p>
          <h2>RACCOMANDAZIONI:</h2>
          <ul>
            ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
          </ul>
          <h2>PUNTEGGI:</h2>
          <ul>
            <li>Evaporativo: ${result.scores.evaporativeScore}</li>
            <li>Deficit Acquoso: ${result.scores.aqueousScore}</li>
            <li>Sintomi Totali: ${result.scores.totalSymptoms}</li>
          </ul>
          <div class="disclaimer">
            <strong>DISCLAIMER:</strong><br>
            Questo risultato non sostituisce una valutazione medica professionale. 
            Porta con te questo risultato alla visita oculistica per una valutazione completa.
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const copyToClipboard = () => {
    const textToCopy = `QUESTIONARIO OCCHIO SECCO - RISULTATO
Data: ${new Date().toLocaleDateString('it-IT')}

CLASSIFICAZIONE: ${result.type}

DESCRIZIONE: ${result.description}

RACCOMANDAZIONI:
${result.recommendations.map((rec, index) => `${index + 1}. ${rec}`).join('\n')}

DISCLAIMER: Questo risultato non sostituisce una valutazione medica. Portalo con te alla visita oculistica.`;

    navigator.clipboard.writeText(textToCopy).then(() => {
      alert('Risultato copiato negli appunti!');
    });
  };

  const restart = () => {
    setCurrentSection(0);
    setAnswers({});
    setShowResults(false);
    setResult(null);
  };

  const isCurrentSectionComplete = () => {
    return sections[currentSection].questions.every(q => answers[q.id] !== undefined);
  };

  const progress = ((currentSection + (isCurrentSectionComplete() ? 1 : 0)) / sections.length) * 100;

  if (showResults) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-blue-600 mb-2">Il tuo Risultato</h1>
              <div className="w-20 h-1 bg-blue-600 mx-auto rounded"></div>
            </div>
            
            <div className="bg-blue-50 border-l-4 border-blue-500 p-6 mb-6 rounded-r-lg">
              <h2 className="text-2xl font-semibold text-blue-800 mb-4">{result.type}</h2>
              <p className="text-gray-700 text-lg leading-relaxed">{result.description}</p>
            </div>

            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <span className="bg-green-100 text-green-800 p-2 rounded-full mr-3">💡</span>
                Raccomandazioni Personalizzate
              </h3>
              <ul className="space-y-3">
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-start">
                <span className="text-yellow-600 text-xl mr-3">⚠️</span>
                <div>
                  <h4 className="font-semibold text-yellow-800 mb-1">Importante</h4>
                  <p className="text-yellow-700 text-sm">
                    Questo risultato non sostituisce una valutazione medica. Porta con te questo risultato alla visita oculistica.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={exportToPDF}
                className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center justify-center"
              >
                📄 Esporta PDF
              </button>
              <button
                onClick={copyToClipboard}
                className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center"
              >
                📋 Copia Risultato
              </button>
              <button
                onClick={restart}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                🔄 Rifai Test
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-blue-600 text-white p-6">
            <h1 className="text-2xl font-bold text-center mb-4">Questionario Occhio Secco</h1>
            <div className="w-full bg-blue-500 rounded-full h-3 mb-2">
              <div 
                className="bg-white h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-center text-blue-100">
              Sezione {currentSection + 1} di {sections.length} • {Math.round(progress)}% completato
            </p>
          </div>

          {/* Content */}
          <div className="p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                {sections[currentSection].title}
              </h2>
              <p className="text-gray-600">{sections[currentSection].description}</p>
            </div>

            <div className="space-y-6">
              {sections[currentSection].questions.map((question, qIndex) => (
                <div key={question.id} className="bg-gray-50 rounded-lg p-6">
                  <div className="mb-4">
                    <span className="text-sm font-semibold text-blue-600">
                      Domanda {(currentSection * sections.slice(0, currentSection).reduce((acc, s) => acc + s.questions.length, 0)) + qIndex + 1}
                    </span>
                    <h3 className="text-lg font-medium text-gray-800 mt-1">
                      {question.text}
                    </h3>
                  </div>

                  {question.type === 'scale' ? (
                    <div className="grid grid-cols-5 gap-2">
                      {[0, 1, 2, 3, 4].map(value => (
                        <button
                          key={value}
                          onClick={() => handleAnswer(question.id, value)}
                          className={`p-3 rounded-lg border-2 transition-all ${
                            answers[question.id] === value
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="font-bold text-lg">{value}</div>
                          <div className="text-xs text-gray-600 mt-1">
                            {scaleLabels[value]}
                          </div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-4">
                      <button
                        onClick={() => handleAnswer(question.id, 'si')}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          answers[question.id] === 'si'
                            ? 'border-green-500 bg-green-50 text-green-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="font-semibold">Sì</div>
                      </button>
                      <button
                        onClick={() => handleAnswer(question.id, 'no')}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          answers[question.id] === 'no'
                            ? 'border-red-500 bg-red-50 text-red-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="font-semibold">No</div>
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Navigation */}
            <div className="flex justify-between mt-8">
              <button
                onClick={prevSection}
                disabled={currentSection === 0}
                className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                  currentSection === 0
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-600 text-white hover:bg-gray-700'
                }`}
              >
                ← Indietro
              </button>
              
              <button
                onClick={nextSection}
                disabled={!isCurrentSectionComplete()}
                className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                  !isCurrentSectionComplete()
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : currentSection === sections.length - 1
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {currentSection === sections.length - 1 ? 'Calcola Risultato' : 'Avanti →'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
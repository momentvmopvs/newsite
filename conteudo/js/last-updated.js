  // Pega a data de modificação do documento
  const lastUpdated = new Date(document.lastModified);

  // Formata para dia/mês/ano e hora:minuto
  const options = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };

  // Exibe no elemento <span id="last-updated">
  document.getElementById("last-updated").textContent = 
    lastUpdated.toLocaleDateString("pt-BR", options).replace(",", " |");
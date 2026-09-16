/* =========================================================
   FORMULÁRIO DE ORÇAMENTO — Momentvm Opvs
   Não calcula nem exibe preço: apenas coleta especificações
   (serviço, dimensões, quantidade, material, local) para o
   time comercial preparar a proposta depois.
========================================================= */

(function () {
  // CEP da sede da Momentvm Opvs (Av. Eng. Heitor Antonio Eiras Garcia, 6363 — Jd. Esmeralda)
  const ORIGIN_CEP = '05564-200';

  // Aplica um estado visual (carregando / ok / erro) à mensagem, seguindo a tipologia do site
  function setStatus(el, text, state) {
    if (!el) return;
    el.textContent = text;
    el.classList.remove('status-carregando', 'status-ok', 'status-erro');
    if (state) el.classList.add('status-' + state);
  }

  const lista = document.getElementById('orc-servicos-lista');
  const template = document.getElementById('orc-servico-template');
  const addBtn = document.getElementById('orc-add-servico');

  // Serviço pré-selecionado ao chegar de uma página específica (?servico=Fachada+em+ACM)
  const servicoPreSelecionado = new URLSearchParams(window.location.search).get('servico');

  if (lista && template && addBtn) {
    const addServiceRow = () => {
      const node = template.content.cloneNode(true);
      if (servicoPreSelecionado && !lista.querySelector('.orc-servico-row')) {
        const select = node.querySelector('select');
        const opcao = Array.from(select.options).find((o) => o.value === servicoPreSelecionado);
        if (opcao) select.value = servicoPreSelecionado;
      }
      lista.appendChild(node);
      atualizarBotoesRemover();
    };

    function atualizarBotoesRemover() {
      const linhas = lista.querySelectorAll('.orc-servico-row');
      linhas.forEach((linha) => {
        const btn = linha.querySelector('.b2b-form-btn-remover');
        btn.style.display = linhas.length > 1 ? 'block' : 'none';
      });
    }

    lista.addEventListener('click', (e) => {
      if (e.target.classList.contains('b2b-form-btn-remover')) {
        const linhas = lista.querySelectorAll('.orc-servico-row');
        if (linhas.length > 1) {
          e.target.closest('.orc-servico-row').remove();
          atualizarBotoesRemover();
        }
      }
    });

    addBtn.addEventListener('click', addServiceRow);

    // Primeira linha já vem preenchida ao carregar a página
    addServiceRow();
  }

  // ---- CEP → preenchimento automático de endereço (ViaCEP) ----
  const cepInput = document.getElementById('orc-cep');
  const cepStatus = document.getElementById('orc-cep-status');
  const ruaInput = document.getElementById('orc-rua');
  const bairroInput = document.getElementById('orc-bairro');
  const cidadeInput = document.getElementById('orc-cidade');
  const ufInput = document.getElementById('orc-uf');
  const numeroInput = document.getElementById('orc-numero');

  if (cepInput) {
    cepInput.addEventListener('input', () => {
      // Aplica a máscara 00000-000 enquanto a pessoa digita
      let digits = cepInput.value.replace(/\D/g, '').slice(0, 8);
      cepInput.value = digits.length > 5 ? digits.slice(0, 5) + '-' + digits.slice(5) : digits;
    });

    cepInput.addEventListener('blur', async () => {
      const digits = cepInput.value.replace(/\D/g, '');
      if (digits.length !== 8) return;

      setStatus(cepStatus, 'Buscando endereço...', 'carregando');
      try {
        const r = await fetch(`https://viacep.com.br/ws/${digits}/json/`);
        if (!r.ok) throw new Error('viacep');
        const d = await r.json();
        if (d.erro) throw new Error('cep não encontrado');

        ruaInput.value = d.logradouro || '';
        bairroInput.value = d.bairro || '';
        cidadeInput.value = d.localidade || '';
        ufInput.value = d.uf || '';
        setStatus(cepStatus, 'Endereço encontrado — confirme e preencha o número.', 'ok');
        if (numeroInput) numeroInput.focus();
      } catch (err) {
        setStatus(cepStatus, 'Não encontramos esse CEP — preencha o endereço manualmente.', 'erro');
      }
    });
  }

  // ---- Distância até a base (apenas informação de logística, sem custo) ----
  const calcularBtn = document.getElementById('orc-calcular-distancia');
  const statusEl = document.getElementById('orc-distancia-status');
  const kmInput = document.getElementById('orc-distancia-km');
  const enderecoCompletoInput = document.getElementById('orc-endereco-completo');

  function montarEnderecoLegivel() {
    const partes = [
      [ruaInput?.value, numeroInput?.value].filter(Boolean).join(', '),
      bairroInput?.value,
      cidadeInput?.value && ufInput?.value ? `${cidadeInput.value} - ${ufInput.value}` : cidadeInput?.value,
    ].filter(Boolean);
    return partes.join(', ');
  }

  // Geocodifica via Photon (base do OpenStreetMap, com CORS liberado para uso em sites —
  // o Nominatim direto bloqueia esse tipo de chamada vinda do navegador)
  async function geocodePhoton(query) {
    const r = await fetch('https://photon.komoot.io/api/?limit=1&q=' + encodeURIComponent(query));
    if (!r.ok) throw new Error('geocode');
    const d = await r.json();
    const feature = d.features && d.features[0];
    if (!feature) throw new Error('endereço não encontrado no mapa');
    return feature.geometry.coordinates; // [lon, lat]
  }

  function geocodeByCEP(cep, cidade) {
    const digits = String(cep).replace(/\D/g, '');
    const cepFormatado = digits.slice(0, 5) + '-' + digits.slice(5);
    return geocodePhoton(`${cepFormatado} ${cidade || ''} Brasil`.trim());
  }

  // Alternativa: geocodifica por rua + cidade + estado (usado se o CEP não tiver match no mapa)
  function geocodeByStreet() {
    const partes = [
      [ruaInput?.value, numeroInput?.value].filter(Boolean).join(' '),
      cidadeInput?.value,
      ufInput?.value,
      'Brasil',
    ].filter(Boolean);
    return geocodePhoton(partes.join(', '));
  }

  if (calcularBtn) {
    calcularBtn.addEventListener('click', async () => {
      const cepDigits = (cepInput?.value || '').replace(/\D/g, '');
      const enderecoLegivel = montarEnderecoLegivel();

      if (enderecoCompletoInput) {
        enderecoCompletoInput.value = [enderecoLegivel, cepInput?.value].filter(Boolean).join(' — CEP ');
      }

      if (cepDigits.length !== 8 && !cidadeInput?.value) {
        setStatus(statusEl, 'Preencha ao menos o CEP (ou cidade e estado) antes de calcular.', 'erro');
        return;
      }

      setStatus(statusEl, 'Calculando...', 'carregando');
      try {
        const origem = await geocodeByCEP(ORIGIN_CEP, 'São Paulo');

        let destino;
        try {
          destino = cepDigits.length === 8
            ? await geocodeByCEP(cepDigits, cidadeInput?.value)
            : await geocodeByStreet();
        } catch (e) {
          // Se a busca por CEP falhar, tenta por rua/cidade/estado como alternativa
          destino = await geocodeByStreet();
        }

        const r = await fetch(
          `https://router.project-osrm.org/route/v1/driving/${origem[0]},${origem[1]};${destino[0]},${destino[1]}?overview=false`
        );
        if (!r.ok) throw new Error('rota');
        const d = await r.json();
        if (!d.routes || !d.routes[0]) throw new Error('rota não encontrada');

        const km = (d.routes[0].distance / 1000).toFixed(1);
        kmInput.value = km;
        setStatus(
          statusEl,
          `Aproximadamente ${km} km da nossa base — essa informação ajuda nosso time a planejar o deslocamento da equipe.`,
          'ok'
        );
      } catch (err) {
        setStatus(
          statusEl,
          'Não conseguimos calcular automaticamente. Sem problema, nosso time confirma a distância com você.',
          'erro'
        );
      }
    });
  }
})();

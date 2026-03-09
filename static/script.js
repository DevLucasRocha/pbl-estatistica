document.addEventListener("DOMContentLoaded", () => {
    const btnAuditoria = document.getElementById("run-audit-btn");
    const dashboard = document.getElementById("dashboard");
    
    btnAuditoria.addEventListener("click", () => {
        btnAuditoria.textContent = "Processando Auditoria...";
        btnAuditoria.disabled = true;

        fetch("/api/auditoria")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erro na resposta do servidor");
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert("Erro ao processar auditoria: " + data.error);
                    return;
                }
                
                populateDashboard(data);
                dashboard.classList.remove("hidden");
                // Scroll to results
                dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            })
            .catch(error => {
                console.error("Erro na requisição:", error);
                alert("Falha de comunicação com a API. Verifique se o backend está rodando.");
            })
            .finally(() => {
                btnAuditoria.textContent = "Atualizar Auditoria";
                btnAuditoria.disabled = false;
            });
    });

    function populateDashboard(data) {
        // Formatar números para 2 casas decimais + %
        const fmt = (num) => typeof num === "number" ? num.toFixed(2) + '%' : '0.00%';

        // 1. Veredito
        const verdictCard = document.getElementById("verdict-card");
        const verdictTitle = document.getElementById("verdict-title");
        const verdictDetails = document.getElementById("verdict-details");
        
        verdictCard.className = "verdict-section"; // reset
        
        if (data.verificacao.veredito === "Indícios de Fraude") {
            verdictCard.classList.add("danger");
            verdictTitle.textContent = "Status: Indícios de Fraude Detectados";
        } else {
            verdictCard.classList.add("safe");
            verdictTitle.textContent = "Status: Seguro (Normalidade)";
        }
        
        let detailsHtml = `Coeficiente de Variação (CV): <span style="font-weight: 700;">${fmt(data.dispersao.coeficiente_variacao)}</span>`;
        if (data.verificacao.tem_outlier) {
            detailsHtml += ` <br><span style="color: var(--danger-color); font-weight: 700;">Atenção: Margens operacionais acima de 100% detectadas (Outliers)</span>`;
        } else {
            detailsHtml += ` | Nenhuma margem acima de 100% detectada.`;
        }
        verdictDetails.innerHTML = detailsHtml;

        // 2. Tendência Central
        document.getElementById("val-media").textContent = fmt(data.tendencia_central.media);
        document.getElementById("val-media-geom").textContent = fmt(data.tendencia_central.media_geometrica);
        document.getElementById("val-media-harm").textContent = fmt(data.tendencia_central.media_harmonica);
        document.getElementById("val-mediana").textContent = fmt(data.tendencia_central.mediana);
        document.getElementById("val-moda").textContent = fmt(data.tendencia_central.moda);

        // 3. Dispersão
        document.getElementById("val-mad").textContent = fmt(data.dispersao.desvio_absoluto_medio);
        document.getElementById("val-variancia").textContent = (data.dispersao.variancia).toFixed(2);
        document.getElementById("val-desvio").textContent = fmt(data.dispersao.desvio_padrao);
        document.getElementById("val-cv").textContent = fmt(data.dispersao.coeficiente_variacao);

        // 4. Quartis e Percentis Table
        const quartisBody = document.getElementById("quartis-tbody");
        quartisBody.innerHTML = `
            <tr><td>p10 (Percentil 10)</td><td>${fmt(data.posicao.percentis.p10)}</td></tr>
            <tr><td>Q1 (Quartil 1 - 25%)</td><td>${fmt(data.posicao.quartis.Q1)}</td></tr>
            <tr><td>Q2 (Mediana - 50%)</td><td>${fmt(data.posicao.quartis.Q2)}</td></tr>
            <tr><td>Q3 (Quartil 3 - 75%)</td><td>${fmt(data.posicao.quartis.Q3)}</td></tr>
            <tr><td>p90 (Percentil 90)</td><td>${fmt(data.posicao.percentis.p90)}</td></tr>
        `;

        // 5. Decis Table
        const decisBody = document.getElementById("decis-tbody");
        decisBody.innerHTML = "";
        for (let i = 1; i <= 9; i++) {
            decisBody.innerHTML += `<tr><td>D${i} (Decil ${i} - ${i}0%)</td><td>${fmt(data.posicao.decis[`D${i}`])}</td></tr>`;
        }
    }
});

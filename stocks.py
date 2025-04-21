import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
import time

st.set_page_config(page_title="Estudo de Mercado", layout="wide")
st.title("📈 Estudo de Mercado - Análise Técnica e Fundamental")

LIMITES = {
    "RSI": 55,
    "P/E": 30,
    "P/B": 3,
    "ROE": 0.10,
    "D/E": 4
}

@st.cache_data
def obter_tickers_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    return tables[0]['Symbol'].tolist()

@st.cache_data
def obter_tickers_europa():
    return [
        "ASML.AS", "AD.AS", "PHIA.AS", "HEIA.AS", "URW.AS", "DSM.AS", "AKZA.AS", "MT.AS", "KPN.AS", "RAND.AS",
        "AIR.PA", "AI.PA", "OR.PA", "BN.PA", "MC.PA", "CAP.PA", "ENGI.PA", "VIE.PA", "SAN.PA", "SU.PA",
        "ABI.BR", "KBC.BR", "UCB.BR", "SOLB.BR", "COFB.BR", "AGEAS.BR", "BPOST.BR", "ACKB.BR", "EVS.BR", "GBLB.BR",
        "GALP.LS", "EDP.LS", "EDPR.LS", "JMT.LS", "BCP.LS", "CTT.LS", "ALTR.LS", "NVG.LS", "SON.LS", "SEM.LS",
        "ISP.MI", "ENI.MI", "STM.MI", "MB.MI", "TEN.MI", "ATL.MI", "BMED.MI", "UCG.MI", "LUX.MI", "CNHI.MI",
        "BMW.DE", "BAS.DE", "BAYN.DE", "SAP.DE", "SIE.DE", "DTE.DE", "DBK.DE", "ALV.DE", "FME.DE", "RWE.DE",
        "NOVN.SW", "NESN.SW", "ROG.SW", "ZURN.SW", "CSGN.SW", "SGSN.SW", "UBSG.SW", "ADEN.SW", "SREN.SW", "LONN.SW",
        "IBE.MC", "ITX.MC", "BBVA.MC", "SAN.MC", "REP.MC", "ACS.MC", "FER.MC", "TEF.MC", "GRF.MC", "MAP.MC",
        "AZN.L", "HSBA.L", "BP.L", "GSK.L", "RIO.L", "ULVR.L", "VOD.L", "BATS.L", "LSEG.L", "DGE.L",
        "NVO"
    ]

def aplicar_criterios_tecnicos(df):
    close = df['Close'].squeeze()
    volume = df['Volume'].squeeze()
    df['RSI'] = RSIIndicator(close=close).rsi()
    macd = MACD(close=close)
    df['MACD'] = macd.macd()
    df['MACD_Sinal'] = macd.macd_signal()
    df['SMA50'] = close.rolling(window=50).mean()
    df['Volume_Media20'] = volume.rolling(window=20).mean()
    rsi = float(df['RSI'].iloc[-1])
    macd_val = float(df['MACD'].iloc[-1])
    macd_sinal = float(df['MACD_Sinal'].iloc[-1])
    sma50 = float(df['SMA50'].iloc[-1])
    vol = float(df['Volume'].iloc[-1])
    vol_med = float(df['Volume_Media20'].iloc[-1])
    preco = float(close.iloc[-1])
    resultado = {
        "Preço": round(preco, 2),
        "RSI (⏬ <55)": f"{rsi:.2f} ✅" if rsi < LIMITES["RSI"] else f"{rsi:.2f} ❌",
        "MACD > Sinal?": "✅" if macd_val > macd_sinal else "❌",
        "Preço > SMA50?": "✅" if preco > sma50 else "❌",
        "Volume > Médio20? (bónus)": "✅" if vol > vol_med else "❌"
    }
    tecnica_ok = rsi < LIMITES["RSI"] and macd_val > macd_sinal and preco > sma50
    return tecnica_ok, resultado

def analisar_fundamentais(ticker):
    try:
        info = yf.Ticker(ticker).info
        pe = info.get('trailingPE')
        pb = info.get('priceToBook')
        roe = info.get('returnOnEquity')
        de = info.get('debtToEquity')
        resultado = {
            "P/E (<30)": f"{pe:.2f} ✅" if pe is not None and pe < LIMITES["P/E"] else f"{pe:.2f} ❌" if pe else "N/A",
            "P/B (<3)": f"{pb:.2f} ✅" if pb is not None and pb < LIMITES["P/B"] else f"{pb:.2f} ❌" if pb else "N/A",
            "ROE (>10%)": f"{roe*100:.1f}% ✅" if roe is not None and roe > LIMITES["ROE"] else f"{roe*100:.1f}% ❌" if roe else "N/A",
            "D/E (<4) (opcional)": f"{de:.2f} ✅" if de is not None and de < LIMITES["D/E"] else f"{de:.2f} ❌" if de else "N/A"
        }
        fundamental_ok = all([
            pe is not None and pe < LIMITES["P/E"],
            pb is not None and pb < LIMITES["P/B"],
            roe is not None and roe > LIMITES["ROE"]
        ])
        return fundamental_ok, resultado
    except:
        return False, {}

with st.expander("📘 Critérios"):
    st.markdown("""
### 📊 Indicadores Técnicos

---

#### **RSI (Índice de Força Relativa)**
Mede a velocidade e a mudança dos movimentos de preços. Ajuda a identificar condições de sobrecompra ou sobrevenda.

| Intervalo     | Interpretação |
|---------------|----------------|
| 🟢 **< 30**    | Sobrevendida, sinal de compra |
| 🟡 **30–70**   | Zona neutra     |
| 🔴 **> 70**    | Sobrecomprada, risco de correção |

---

#### **MACD (Moving Average Convergence Divergence)**
Mostra a relação entre duas médias móveis exponenciais, útil para identificar mudanças de tendência.

| Condição         | Interpretação |
|------------------|---------------|
| 🟢 **MACD > Sinal** | Tendência positiva, entrada possível |
| 🔴 **MACD < Sinal** | Tendência negativa ou neutra |

---

#### **SMA50 (Média Móvel Simples 50 dias)**
Representa a média de preços de 50 dias. Mostra a direção geral da tendência.

| Condição               | Interpretação |
|------------------------|---------------|
| 🟢 **Preço > SMA50**   | Tendência de alta |
| 🔴 **Preço < SMA50**   | Tendência de baixa |

---

#### **Volume vs Volume Médio (20 dias)**
Compara o volume atual com a média dos últimos 20 dias. Reflete o interesse dos investidores.

| Condição                | Interpretação |
|-------------------------|----------------|
| 🟢 **Volume > Média20** | Interesse crescente (positivo) |
| 🔴 **Volume < Média20** | Interesse fraco |

---

### 📈 Indicadores Fundamentais

---

#### **P/E (Preço / Lucro por Ação)**
Quanto os investidores estão a pagar por cada unidade de lucro.

| Intervalo     | Interpretação |
|---------------|----------------|
| 🟢 **< 15**    | Muito atrativo |
| 🟡 **15–30**   | Razoável        |
| 🔴 **> 30**    | Potencialmente caro |

---

#### **P/B (Preço / Valor Contabilístico)**
Compara o preço da ação com o valor dos ativos.

| Intervalo     | Interpretação |
|---------------|----------------|
| 🟢 **< 1.5**   | Pode estar subvalorizada |
| 🟡 **1.5–3**   | Dentro da média |
| 🔴 **> 3**     | Potencialmente sobrevalorizada |

---

#### **ROE (Return on Equity)**
Rentabilidade do capital próprio investido.

| Intervalo     | Interpretação |
|---------------|----------------|
| 🟢 **> 15%**   | Muito rentável |
| 🟡 **10–15%**  | Boa rentabilidade |
| 🔴 **< 10%**   | Rentabilidade fraca |

---

#### **D/E (Dívida / Capital Próprio)**
Mostra a dependência da empresa em relação à dívida.

| Intervalo     | Interpretação |
|---------------|----------------|
| 🟢 **< 1**     | Excelente controlo de dívida |
| 🟡 **1–2**     | Alavancagem moderada |
| 🔴 **> 2**     | Risco financeiro elevado |
""")

col1, col2 = st.columns(2)
st.sidebar.title("⚙️ Controlo")

if 'analise_em_curso' not in st.session_state:
    st.session_state['analise_em_curso'] = False
if 'tickers' not in st.session_state:
    st.session_state['tickers'] = []
if 'resultados' not in st.session_state:
    st.session_state['resultados'] = []
if 'indice' not in st.session_state:
    st.session_state['indice'] = 0

if st.sidebar.button("🛑 Parar análise"):
    st.session_state['analise_em_curso'] = False

if st.sidebar.button("▶️ Retomar análise"):
    st.session_state['analise_em_curso'] = True

if col1.button("🇺🇸 Analisar S&P 500"):
    st.session_state['tickers'] = obter_tickers_sp500()
    st.session_state['analise_em_curso'] = True
    st.session_state['resultados'] = []
    st.session_state['indice'] = 0

if col2.button("🇪🇺 Analisar Europa"):
    st.session_state['tickers'] = obter_tickers_europa()
    st.session_state['analise_em_curso'] = True
    st.session_state['resultados'] = []
    st.session_state['indice'] = 0

if st.session_state['analise_em_curso']:
    barra = st.progress(0)
    for i in range(st.session_state['indice'], len(st.session_state['tickers'])):
        ticker = st.session_state['tickers'][i]
        st.write(f"🔍 A analisar {ticker}...")
        try:
            df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False, progress=False)
            if df.empty:
                continue
            df.dropna(inplace=True)
            tecnica, res_tec = aplicar_criterios_tecnicos(df)
            fundamental, res_fund = analisar_fundamentais(ticker)
            st.session_state['resultados'].append({
                "Ticker": ticker,
                "✔ Técnica": "✅" if tecnica else "❌",
                "✔ Fundamental": "✅" if fundamental else "❌",
                **res_tec,
                **res_fund
            })
        except Exception as e:
            st.warning(f"Erro ao processar {ticker}: {e}")
        st.session_state['indice'] = i + 1
        barra.progress((i + 1) / len(st.session_state['tickers']))
        time.sleep(0.3)
        if not st.session_state['analise_em_curso']:
            st.warning("🛑 Análise interrompida. Podes retomá-la a qualquer momento.")
            break
    else:
        st.session_state['analise_em_curso'] = False
        st.success("✅ Análise concluída!")

if st.session_state['resultados']:
    df_final = pd.DataFrame(st.session_state['resultados'])
    st.dataframe(df_final, use_container_width=True)

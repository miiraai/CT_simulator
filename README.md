# CT Simulator

**CT Simulator** to aplikacja edukacyjna i badawcza umożliwiająca symulację i analizę procesu tomografii komputerowej (CT) w środowisku Python. Projekt pozwala na wizualne przedstawienie procesu skanowania, rekonstrukcji obrazu i manipulacji parametrami tomografu, a także obsługę rzeczywistych danych medycznych w formacie DICOM.

## Główne funkcjonalności

1. **Symulacja procesu skanowania CT**
   - Generowanie danych projekcyjnych (sinogramów) na podstawie obrazu wejściowego.
   - Symulacja ruchu rotacyjnego oraz działania detektorów.

2. **Rekonstrukcja obrazu**
   - Implementacja algorytmów rekonstrukcyjnych (m.in. Filtered Back Projection).
   - Porównanie wyników rekonstrukcji przy różnych parametrach.

3. **Modyfikacja parametrów symulacji**
   - Możliwość dostosowania liczby detektorów, rozdzielczości, zakresu i kroku rotacji, filtrów itd.

4. **Wizualizacja danych**
   - Intuicyjny interfejs graficzny zbudowany w Streamlit.
   - Prezentacja oryginalnych obrazów, sinogramów oraz zrekonstruowanych wyników.

5. **Obsługa formatu DICOM**
   - Wczytywanie i wyświetlanie rzeczywistych danych medycznych przy pomocy biblioteki `pydicom`.

## 🛠️ Wymagania systemowe

- **Python**: 3.8 lub nowszy
- **Biblioteki Python**:
  - `numpy`
  - `matplotlib`
  - `scipy`
  - `streamlit`
  - `pydicom`
 
## Autorzy
- Mateusz Górecki
- Igor Taciak

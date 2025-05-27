Instruções:
 
Para mexer na biblioteca, deem um
 
git clone https://github.com/121lipe121/biblioteca_dijur.git
 
Com isso você pode fazer alterações/adições de funções, depois é só dar commit + push para atualizar, igual um repositório normal, porem não esqueça de mudar a versão no setup.py caso você faça uma atualização, se não o pip install --upgrade não vai identificar que a biblioteca atualizou
 
Uso:
 
Para baixar:
 
pip install git+https://github.com/121lipe121/biblioteca_dijur.git
 
E então pip list para conferir se baixou, como ele baixado basta usar nos projetos:
 
from apiDijur.<pasta> import <função>
 
Por exemplo:
 
from apiDijur.api import hello
 
Para atualizar quando nós fizermos alterações/adições de funções:
 
pip install --upgrade git+https://github.com/121lipe121/biblioteca_dijur.git
import pygame
import os

class Audio:
    def __init__(self, config):
        self.config = config
        self.ativo = config.getboolean('Audio', 'activo')
        
        if self.ativo:
            pygame.mixer.init()
    
    def play_som(self, tipo):
        """Reproduz som conforme tipo"""
        if not self.ativo:
            return
        
        try:
            if tipo == 'venda':
                arquivo = self.config.get('Audio', 'som_venda')
            elif tipo == 'erro':
                arquivo = self.config.get('Audio', 'som_erro')
            else:
                return
            
            if os.path.exists(arquivo):
                pygame.mixer.music.load(arquivo)
                pygame.mixer.music.play()
                
        except Exception as e:
            print(f"Erro ao reproduzir áudio: {e}")
#!/usr/bin/env python3
"""
Benchmark simple et direct des qualités audio
Teste différents bitrates avec ffmpeg directement
"""

import os
import subprocess
import time
import json
from pathlib import Path

class SimpleAudioBenchmark:
    def __init__(self, test_dir="Test", output_dir="benchmark_output"):
        self.test_dir = Path(test_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Qualités à tester
        self.qualities = [
            {"name": "Haute", "bitrate": "192k"},
            {"name": "Moyenne-Haute", "bitrate": "128k"},
            {"name": "Moyenne", "bitrate": "96k"},
            {"name": "Basse", "bitrate": "64k"},
        ]
        
        self.results = []
    
    def get_audiobook_dirs(self):
        """Récupère les dossiers d'audiobooks"""
        audiobooks = []
        for item in self.test_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                audio_files = list(item.rglob("*.mp3")) + list(item.rglob("*.m4a"))
                if audio_files:
                    audiobooks.append(item)
        return audiobooks[:2]  # Teste sur les 2 premiers
    
    def calculate_input_size(self, audiobook_dir):
        """Calcule la taille totale des fichiers audio"""
        total_size = 0
        audio_files = list(audiobook_dir.rglob("*.mp3")) + list(audiobook_dir.rglob("*.m4a"))
        for audio_file in audio_files:
            total_size += audio_file.stat().st_size
        return total_size / (1024*1024)  # MB
    
    def test_quality(self, audiobook_dir, quality):
        """Teste une qualité spécifique avec ffmpeg direct"""
        print(f"\n🎵 Test {quality['name']} ({quality['bitrate']}) sur {audiobook_dir.name}")
        
        # Calcule la taille d'entrée
        input_size = self.calculate_input_size(audiobook_dir)
        
        # Crée la filelist
        audio_files = sorted(list(audiobook_dir.rglob("*.mp3")) + list(audiobook_dir.rglob("*.m4a")))
        filelist_path = f"/tmp/filelist_{audiobook_dir.name.replace(' ', '_')}_{quality['bitrate']}.txt"
        
        with open(filelist_path, 'w') as f:
            for audio_file in audio_files:
                abs_path = str(audio_file.absolute())
                f.write(f"file '{abs_path}'\n")
        
        # Nom du fichier de sortie
        output_name = f"{audiobook_dir.name}_{quality['bitrate']}.m4b"
        output_path = self.output_dir / output_name
        
        # Commande ffmpeg directe
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', filelist_path,
            '-c:a', 'aac', '-b:a', quality['bitrate'],
            '-ar', '44100', '-ac', '2',
            '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5',  # Normalisation
            '-f', 'mp4',
            str(output_path)
        ]
        
        print(f"   📊 {input_size:.1f}MB → ?")
        
        # Lance la conversion
        start_time = time.time()
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Suivi simple
            last_size = 0
            while process.poll() is None:
                if output_path.exists():
                    current_size = output_path.stat().st_size / (1024*1024)
                    if current_size > last_size + 5:  # Affiche chaque 5MB
                        print(f"   📊 {current_size:.1f}MB...")
                        last_size = current_size
                time.sleep(2)
            
            # Attend la fin
            stdout, stderr = process.communicate()
            end_time = time.time()
            
            if process.returncode == 0 and output_path.exists():
                # Calcule les résultats
                output_size = output_path.stat().st_size / (1024*1024)
                duration = end_time - start_time
                compression_ratio = (1 - output_size / input_size) * 100
                
                result = {
                    "audiobook": audiobook_dir.name,
                    "quality": quality['name'],
                    "bitrate": quality['bitrate'],
                    "input_size_mb": round(input_size, 1),
                    "output_size_mb": round(output_size, 1),
                    "compression_percent": round(compression_ratio, 1),
                    "duration_seconds": round(duration, 1),
                    "speed_mbps": round(output_size / duration if duration > 0 else 0, 2)
                }
                
                print(f"   ✅ {input_size:.1f}MB → {output_size:.1f}MB ({compression_ratio:.1f}% compression)")
                print(f"   ⏱️ {duration:.1f}s à {result['speed_mbps']:.2f}MB/s")
                
                return result
            else:
                print(f"   ❌ Erreur: {stderr[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
        finally:
            # Nettoie
            if os.path.exists(filelist_path):
                os.remove(filelist_path)
    
    def run_benchmark(self):
        """Lance le benchmark complet"""
        print("🚀 BENCHMARK QUALITÉ VS TAILLE (SIMPLE)")
        print("=" * 50)
        
        audiobooks = self.get_audiobook_dirs()
        print(f"📚 Test sur {len(audiobooks)} audiobooks:")
        for ab in audiobooks:
            size = self.calculate_input_size(ab)
            print(f"   - {ab.name}: {size:.1f}MB")
        
        total_input_size = sum(self.calculate_input_size(ab) for ab in audiobooks)
        print(f"\n📊 Taille totale: {total_input_size:.1f}MB")
        
        # Teste chaque qualité sur chaque audiobook
        for audiobook in audiobooks:
            print(f"\n🎧 {audiobook.name}")
            print("-" * 40)
            
            for quality in self.qualities:
                result = self.test_quality(audiobook, quality)
                if result:
                    self.results.append(result)
        
        # Affiche les résultats
        self.print_results()
        
        # Sauvegarde les résultats
        self.save_results()
    
    def print_results(self):
        """Affiche les résultats du benchmark"""
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS DU BENCHMARK")
        print("=" * 60)
        
        # Regroupe par qualité
        quality_stats = {}
        for result in self.results:
            quality = result['quality']
            if quality not in quality_stats:
                quality_stats[quality] = []
            quality_stats[quality].append(result)
        
        # Affiche par qualité
        for quality_name, results in quality_stats.items():
            avg_input = sum(r['input_size_mb'] for r in results) / len(results)
            avg_output = sum(r['output_size_mb'] for r in results) / len(results)
            avg_compression = sum(r['compression_percent'] for r in results) / len(results)
            avg_speed = sum(r['speed_mbps'] for r in results) / len(results)
            
            print(f"\n🎵 {quality_name} ({results[0]['bitrate']})")
            print(f"   📊 Taille: {avg_input:.1f}MB → {avg_output:.1f}MB")
            print(f"   🗜️  Compression: {avg_compression:.1f}%")
            print(f"   ⚡ Vitesse: {avg_speed:.2f}MB/s")
        
        # Recommandation
        print(f"\n🎯 RECOMMANDATION:")
        best_quality = None
        best_score = 0
        
        for quality_name, results in quality_stats.items():
            avg_compression = sum(r['compression_percent'] for r in results) / len(results)
            avg_speed = sum(r['speed_mbps'] for r in results) / len(results)
            
            # Score: compression + vitesse (priorité à la compression)
            score = avg_compression + (avg_speed / 20)
            
            print(f"   {quality_name}: {score:.1f} points")
            
            if score > best_score:
                best_score = score
                best_quality = quality_name
        
        print(f"\n   🏆 Meilleur équilibre: {best_quality}")
        print(f"   📈 Score: {best_score:.1f}")
        
        # Vérification taille totale
        total_input = sum(r['input_size_mb'] for r in self.results)
        total_output = sum(r['output_size_mb'] for r in self.results)
        print(f"\n📊 BILAN GLOBAL:")
        print(f"   📥 Entrée totale: {total_input:.1f}MB")
        print(f"   📤 Sortie totale: {total_output:.1f}MB")
        
        if total_input > 0:
            print(f"   🗜️  Compression globale: {(1 - total_output/total_input)*100:.1f}%")
            
            if total_output > total_input:
                print(f"   ⚠️  ATTENTION: La sortie est plus grande que l'entrée !")
            else:
                print(f"   ✅ Compression efficace: {total_input - total_output:.1f}MB économisés")
        else:
            print(f"   ℹ️  Aucun résultat à analyser")
    
    def save_results(self):
        """Sauvegarde les résultats en JSON"""
        results_file = self.output_dir / "benchmark_results.json"
        
        # Regroupe par qualité
        quality_stats = {}
        for result in self.results:
            quality = result['quality']
            if quality not in quality_stats:
                quality_stats[quality] = []
            quality_stats[quality].append(result)
        
        with open(results_file, 'w') as f:
            json.dump(quality_stats, f, indent=2)
        
        print(f"\n💾 Résultats sauvegardés dans: {results_file}")

if __name__ == "__main__":
    benchmark = SimpleAudioBenchmark()
    benchmark.run_benchmark()

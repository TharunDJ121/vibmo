import chromadb
from typing import List, Dict, Any, Tuple
import os
import uuid

class RAGDatabase:
    """
    Manages local ChromaDB collections for Vibmo Agentic Video Editing.
    Stores both Video Media (timestamped chunks) and Vibmo Assets/Tools (Code-RAG).
    """
    def __init__(self, persist_directory: str = ".vibmo_chromadb"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Collection for Code-RAG (Vibmo components, snippets, syntax)
        self.asset_col = self.client.get_or_create_collection(
            name="vibmo_assets",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Collection for Video Media (timestamped b-roll/footage)
        self.media_col = self.client.get_or_create_collection(
            name="video_media",
            metadata={"hnsw:space": "cosine"}
        )

    def seed_vibmo_assets(self):
        """Seeds the database with core Vibmo classes, templates, and Remocn suites."""
        assets = [
            {
                "id": "asset_glasscard",
                "document": "GlassCard is a UI container with glassmorphism, blur, and border effects. Used for modern SaaS dashboards and UI mockups. Parameters: direction, padding, corner_radius, blur_radius.",
                "metadata": {"type": "component", "class": "GlassCard"}
            },
            {
                "id": "asset_kinetictext",
                "document": "KineticText provides animated typography with physics. Useful for titles and dynamic captions. Methods: reveal_characters, spring_in.",
                "metadata": {"type": "component", "class": "KineticText"}
            },
            {
                "id": "asset_meshgradient",
                "document": "MeshGradientFlow is an animated procedural background. Use this for modern colorful backdrops.",
                "metadata": {"type": "background", "class": "MeshGradientFlow"}
            },
            {
                "id": "asset_cyber_sfx",
                "document": "CyberUiSuite provides procedural UI sound effects like holographic_click() and digital_stutter().",
                "metadata": {"type": "sfx", "class": "CyberUiSuite"}
            },
            # Remocn 6-Beat Product Spine & Turnkey Templates
            {
                "id": "asset_remocn_product_spine",
                "document": "TmplSaasProductDemoSpineSuite & ProductDemoSpine: 6-beat SaaS product video spine (Hook -> Positioning -> Product Reveal -> Features -> Proof -> CTA). Single-line scene builder.",
                "metadata": {"type": "template", "class": "TmplSaasProductDemoSpineSuite", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_changelog",
                "document": "TmplChangelogReleaseSuite: Turnkey video template for software version releases and feature drops with version pills and diff cards.",
                "metadata": {"type": "template", "class": "TmplChangelogReleaseSuite", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_cli_launch",
                "document": "TmplCliDeveloperLaunchSuite: High-impact developer CLI tool launch video with fast terminal execution and tool call badges.",
                "metadata": {"type": "template", "class": "TmplCliDeveloperLaunchSuite", "suite": "remocn"}
            },
            # Remocn UI & SaaS Simulators
            {
                "id": "asset_remocn_claude_code",
                "document": "ClaudeCodeSimulator & TerminalCursorZoom: Authentic terminal simulator with instant step-scrolling (no laggy easing), ANSI syntax colors, and tool call folding.",
                "metadata": {"type": "ui_simulator", "class": "ClaudeCodeSimulator", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_ai_prompt_flow",
                "document": "AiPromptFlow & ModelSelectorPill: Interactive AI prompt composer with model dropdown badges, file attachment pills, and live token stream output.",
                "metadata": {"type": "ui_simulator", "class": "AiPromptFlow", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_checkout_flow",
                "document": "InteractiveCheckoutFlow & PaymentCreditCardField: SaaS payment card with numeric auto-formatting, validation checkmark, interactive spinner, and payment success transition.",
                "metadata": {"type": "ui_simulator", "class": "InteractiveCheckoutFlow", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_social_follow",
                "document": "XFollowCard & GitHubStarsCard: Interactive social proof cards with animated cursor click, ripple effect, and live counter increments (+1).",
                "metadata": {"type": "ui_simulator", "class": "XFollowCard", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_bento_pan",
                "document": "InfiniteBentoPan & BentoGridCard: 2.5D camera drifting across an interactive SaaS Bento Grid dashboard.",
                "metadata": {"type": "ui_simulator", "class": "InfiniteBentoPan", "suite": "remocn"}
            },
            # Remocn WebGL Shaders & Video Post-FX
            {
                "id": "asset_remocn_ascii_render",
                "document": "AsciiRenderFilter & AsciiRenderShader: Real-time WebGL glyph matrix conversion filter converting video frames into dynamic ASCII character art.",
                "metadata": {"type": "shader", "class": "AsciiRenderFilter", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_security_cam",
                "document": "SecurityCamOverlay & CctvSurveillanceHud: CCTV surveillance HUD with live blinking REC dot, timecode, framing brackets, crosshairs, and scanlines.",
                "metadata": {"type": "shader", "class": "SecurityCamOverlay", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_neuro_voronoi",
                "document": "ShaderNeuroNoise & ShaderVoronoiGrid: Procedural neural synapse network and Voronoi cellular animated crystal backdrops.",
                "metadata": {"type": "shader", "class": "ShaderNeuroNoise", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_underwater_ripple",
                "document": "UnderwaterRippleFilter: 2D fluid refraction wave displacement filter with chromatic dispersion.",
                "metadata": {"type": "shader", "class": "UnderwaterRippleFilter", "suite": "remocn"}
            },
            # Remocn Kinetic Typography & Decoders
            {
                "id": "asset_remocn_blur_out_up",
                "document": "BlurOutUpText & BlurOutUpCharacterNode: Upward character drift with progressive gaussian blur dissipation and spring deceleration.",
                "metadata": {"type": "typography", "class": "BlurOutUpText", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_matrix_decode",
                "document": "MatrixDecodeText & MatrixGlyphScrambler: Alphanumeric and cipher glyph scramble settling into target text with lock-in flash.",
                "metadata": {"type": "typography", "class": "MatrixDecodeText", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_rolling_odometer",
                "document": "RollingNumberWheel & SlotMachineRoller: Mechanical vertical tumbler rolling numbers for MRR, KPI metrics, and currency counts.",
                "metadata": {"type": "typography", "class": "RollingNumberWheel", "suite": "remocn"}
            },
            {
                "id": "asset_remocn_inline_pill_takeover",
                "document": "InlinePillTakeoverText & StrikethroughReplaceText: Dynamic accent pill morphing around hero words and animated strikethrough replacement.",
                "metadata": {"type": "typography", "class": "InlinePillTakeoverText", "suite": "remocn"}
            },
            # Remocn Cinematic Transitions
            {
                "id": "asset_remocn_transitions",
                "document": "PushThroughTransition, FocusPullTransition, WhipPanTransition, DitherDissolveTransition: Cinematic scene transitions.",
                "metadata": {"type": "transition", "class": "PushThroughTransition", "suite": "remocn"}
            },
            # Anti-Slop Quality Gate
            {
                "id": "asset_remocn_anti_slop",
                "document": "AntiSlopValidator & AntiSlopReport: Automated quality checker enforcing single-accent discipline, sentence-case headings, and subtle 1px elevation.",
                "metadata": {"type": "quality", "class": "AntiSlopValidator", "suite": "remocn"}
            },
            # Video-Shotcraft 152-Shot Suites & Motion Taxonomies
            {
                "id": "asset_shotcraft_deck_deal",
                "document": "DeckDealFlyIn & DocParkPillDeal: Card dealing physics metaphor with spring acceleration, fanned arc layout, and left document docking with feature pills.",
                "metadata": {"type": "shotcraft", "class": "DeckDealFlyIn", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_spotlight_hero",
                "document": "SpotlightHeroCard & DarkMetallicFloor: Volumetric cone spotlight focused on a hero glass card with brushed metallic reflection floor and clipped specular gleam (Case Law Q4, Q5).",
                "metadata": {"type": "shotcraft", "class": "SpotlightHeroCard", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_interactive_dials",
                "document": "AutolayoutGapDial, ChipGridSelectBlackout, AvatarBracketCarousel, BezierSourceConvergeMerge: Interactive UI parameter dials, chip select with blackout, and bezier convergence.",
                "metadata": {"type": "shotcraft", "class": "AutolayoutGapDial", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_outro_group_photo",
                "document": "OutroGroupPhotoLaunch (Keynote Family Portrait), BrandInkOpen, BraceExpand: Climax finale where all demonstrated feature cards fly in from 4 corners around the brand wordmark (Case Law Q8).",
                "metadata": {"type": "shotcraft", "class": "OutroGroupPhotoLaunch", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_rhythm_cuts",
                "document": "BeatCutAccelerando & PaparazziFlash: 16f -> 12f -> 8f -> 4f rhythmic cut sequencing and camera strobe flashes for high-energy drop moments.",
                "metadata": {"type": "shotcraft", "class": "BeatCutAccelerando", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_beat_sync_audio",
                "document": "BeatSyncGrid & TimelineSFXTable: Musical beat synchronization computing beatF(n) frame grids and aligning peak transient SFX cues to kicks and snares.",
                "metadata": {"type": "audio", "class": "BeatSyncGrid", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_jianying_exporter",
                "document": "JianYingDraftExporter: Exports Vibmo timelines into native CapCut / JianYing desktop draft JSON with microsecond timerange accuracy for subtitle and audio editing.",
                "metadata": {"type": "exporter", "class": "JianYingDraftExporter", "suite": "shotcraft"}
            },
            {
                "id": "asset_shotcraft_aesthetic_case_law",
                "document": "AestheticCaseLawValidator: Production rule auditor enforcing R1-R4 (hold >= 1.0s, slam <= 3), Q1-Q10 (glints <= 1 clipped in radius, keynote outro completeness), and S1-S4.",
                "metadata": {"type": "quality", "class": "AestheticCaseLawValidator", "suite": "shotcraft"}
            },
            # Video-Production-Skills & Dark Magic UI
            {
                "id": "asset_prodskills_dark_magic_stage",
                "document": "DarkStarfieldStage: Pitch black spatial stage with twinkling star dust particles and soft bottom purple horizon glow (#7c3aed) for Presenton-style SaaS videos.",
                "metadata": {"type": "stage", "class": "DarkStarfieldStage", "suite": "production_skills"}
            },
            {
                "id": "asset_prodskills_prompt_invocation",
                "document": "PromptInvocationCard: 2.5D tilted glowing prompt card with live character typing, cyan-to-magenta gradient CTA, click pulse, and particle sparkle burst.",
                "metadata": {"type": "ui_card", "class": "PromptInvocationCard", "suite": "production_skills"}
            },
            {
                "id": "asset_prodskills_model_orbit_export",
                "document": "ModelCapabilityOrbit, ExportBurstContainer, ConnectEcosystemSlot: 3D orbital badge ring, radiating multi-format export bursts (PDF, PPTX, MP4, API), and curved ecosystem slot nodes.",
                "metadata": {"type": "ui_cluster", "class": "ModelCapabilityOrbit", "suite": "production_skills"}
            },
            {
                "id": "asset_prodskills_tmpl_dark_saas",
                "document": "TmplDarkSaasMagicSuite: Turnkey 8-blueprint Presenton-style Dark SaaS promo video generator with starfield stage, prompt typing, model orbit, and export burst.",
                "metadata": {"type": "template", "class": "TmplDarkSaasMagicSuite", "suite": "production_skills"}
            },
            {
                "id": "asset_prodskills_bw_typing_opener",
                "document": "BlackWhiteTypingOpener: Pure black stage, 14 chars/sec deterministic typewriter reveal, synchronized Foley typing clicks, word replacements, and velocity wipes.",
                "metadata": {"type": "typography", "class": "BlackWhiteTypingOpener", "suite": "production_skills"}
            },
            {
                "id": "asset_prodskills_meta_director",
                "document": "MotionThesis, BeatGraph, BeatNode, AntiPptGate: Continuous motion thesis planning, 7-narrative job beat graph, and Anti-PPT gate rejecting static slide-like videos.",
                "metadata": {"type": "ai_director", "class": "AntiPptGate", "suite": "production_skills"}
            },
            {
                "id": "asset_prodskills_replica_verifier",
                "document": "VideoReplicaVerifier, FidelityLevel: Full-frame video recreation verification via MAE, PSNR, SSIM, boundary frames, and 3-stage evidence gates (Asset, Runtime, Delivery).",
                "metadata": {"type": "quality", "class": "VideoReplicaVerifier", "suite": "production_skills"}
            },
        ]
        
        docs = [a["document"] for a in assets]
        ids = [a["id"] for a in assets]
        metas = [a["metadata"] for a in assets]
        
        # Upsert into Chroma
        self.asset_col.upsert(documents=docs, ids=ids, metadatas=metas)
        print(f"[RAG] Seeded {len(assets)} Vibmo, Remocn, Shotcraft & Production-Skills assets into Code-RAG Vector DB.")

    def index_video_file(self, video_path: str, simulated_descriptions: List[Tuple[float, float, str]]):
        """
        Simulates running a Multimodal Vision model over an mp4.
        Takes a list of (start_time, end_time, description).
        """
        docs = []
        ids = []
        metas = []
        
        for start, end, desc in simulated_descriptions:
            chunk_id = f"{os.path.basename(video_path)}_{start}_{end}"
            docs.append(desc)
            ids.append(chunk_id)
            metas.append({
                "source": video_path,
                "start_time": start,
                "end_time": end
            })
            
        self.media_col.upsert(documents=docs, ids=ids, metadatas=metas)
        print(f"[RAG] Indexed {len(docs)} segments from {video_path}.")

    def search_assets(self, query: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """Queries the Code-RAG for Vibmo components."""
        res = self.asset_col.query(query_texts=[query], n_results=n_results)
        return self._format_results(res)

    def search_media(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Queries the Video Media DB for semantic clips."""
        res = self.media_col.query(query_texts=[query], n_results=n_results)
        return self._format_results(res)
        
    def _format_results(self, chromadb_result: dict) -> List[Dict[str, Any]]:
        if not chromadb_result["documents"]:
            return []
        
        docs = chromadb_result["documents"][0]
        metas = chromadb_result["metadatas"][0]
        
        formatted = []
        for d, m in zip(docs, metas):
            formatted.append({"document": d, "metadata": m})
        return formatted

if __name__ == "__main__":
    # Quick test
    db = RAGDatabase()
    db.seed_vibmo_assets()
    db.index_video_file("raw_broll_forest.mp4", [
        (0.0, 5.0, "Drone shot flying over a dense green pine forest in morning mist."),
        (5.0, 10.0, "Close up of a stream flowing over rocks covered in moss.")
    ])
    
    print("\n--- Testing Search ---")
    print("Code-RAG Search 'animated background':", db.search_assets("animated background", 1))
    print("Media Search 'water flowing':", db.search_media("water flowing", 1))

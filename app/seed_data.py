from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Development, Interaction, Lead, LeadRecommendation, Material, Task, User


def _get_or_create_user(db: Session, name: str, phone: str, role: str, email: str | None = None) -> User:
    user = db.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
    if user:
        user.name = name
        user.role = role
        user.email = email
        return user
    user = User(name=name, phone=phone, role=role, email=email)
    db.add(user)
    db.flush()
    return user


def _get_or_create_development(db: Session, name: str, city: str, description: str, sales_arguments: str) -> Development:
    item = db.execute(select(Development).where(Development.name == name)).scalar_one_or_none()
    if item:
        item.city = city
        item.description = description
        item.sales_arguments = sales_arguments
        item.status = "ativo"
        return item
    item = Development(
        name=name,
        city=city,
        status="ativo",
        description=description,
        sales_arguments=sales_arguments,
    )
    db.add(item)
    db.flush()
    return item


def seed_if_empty(db: Session) -> None:
    """Popula a demo com dados suficientes para a experiência premium."""
    settings = get_settings()
    now = datetime.now(timezone.utc)

    franco = _get_or_create_user(
        db,
        name="Franco",
        phone=settings.default_manager_phone or "5516999990000",
        role="manager",
        email="franco@evora.local",
    )
    brokers = [
        _get_or_create_user(db, "Juliana Ferreira", "5511988776655", "broker", "juliana.ferreira@email.com"),
        _get_or_create_user(db, "Rafael Souza", "5511976543321", "broker", "rafael.souza@email.com"),
        _get_or_create_user(db, "Camila Ribeiro", "5511964210099", "broker", "camila.ribeiro@email.com"),
        _get_or_create_user(db, "Bruno Lima", "5511942137788", "broker", "bruno.lima@email.com"),
        _get_or_create_user(db, "Lucas Andrade", "5516999999999", "manager", "lucas.andrade@evora.local"),
        _get_or_create_user(db, "Carlos Corretor", "5516888888888", "broker", "carlos@evora.local"),
    ]

    developments = {
        "Vila dos Ipês": _get_or_create_development(
            db,
            "Vila dos Ipês",
            "Ribeirão Preto/SP",
            "Residencial planejado com lotes próximos a eixos de crescimento e apelo de moradia familiar.",
            "Qualidade de vida, localização, valorização, infraestrutura completa, escolha de quadra e segurança documental.",
        ),
        "Reserva do Vale": _get_or_create_development(
            db,
            "Reserva do Vale",
            "Sertãozinho/SP",
            "Empreendimento com perfil familiar e ótima relação entre preço, lote e prazo de pagamento.",
            "Entrada facilitada, bairro em crescimento, visita ao decorado e simulação personalizada.",
        ),
        "Solar das Árvores": _get_or_create_development(
            db,
            "Solar das Árvores",
            "Interior/SP",
            "Loteamento residencial com foco em construção futura e valorização de médio prazo.",
            "Planejamento de construção, escolha antecipada de lote, tranquilidade e potencial de revenda.",
        ),
        "Jardins do Lago": _get_or_create_development(
            db,
            "Jardins do Lago",
            "Interior/SP",
            "Projeto com perfil de investimento e expansão urbana.",
            "Liquidez, fase de lançamento, preço por metro, localização e escassez.",
        ),
    }
    db.commit()

    if not db.execute(select(Material).limit(1)).scalar_one_or_none():
        material_rows = [
            ("Vídeo aéreo — Vista geral", "video", "Primeiro contato visual", "video,aereo,institucional", "Vila dos Ipês"),
            ("Mapa de localização", "imagem", "Cliente que não conhece a região", "mapa,localizacao,regiao", "Vila dos Ipês"),
            ("Tabela de unidades — Maio/2025", "pdf", "Cliente qualificado com capacidade financeira", "tabela,unidades,condicoes", "Vila dos Ipês"),
            ("Implantação geral", "imagem", "Cliente comparando lote, quadra e posição", "implantacao,quadras,lotes", "Vila dos Ipês"),
            ("Fotos de obra — Maio/2025", "galeria", "Cliente inseguro com entrega ou infraestrutura", "obra,fotos,infraestrutura", "Reserva do Vale"),
            ("Depoimento — Cliente satisfeita", "video", "Prova social para cliente inseguro", "depoimento,prova-social", "Solar das Árvores"),
            ("FAQ documental", "pdf", "Objeção de segurança jurídica", "documentacao,seguranca,faq", "Vila dos Ipês"),
            ("Argumentos de valorização", "pdf", "Investidor iniciante ou experiente", "investidor,valorizacao,liquidez", "Jardins do Lago"),
        ]
        for title, type_, use_case, tags, dev_name in material_rows:
            db.add(
                Material(
                    development_id=developments[dev_name].id,
                    title=title,
                    type=type_,
                    url="#",
                    use_case=use_case,
                    tags=tags,
                )
            )
        db.commit()

    if not db.execute(select(Lead).limit(1)).scalar_one_or_none():
        lead_rows = [
            {
                "name": "Juliana Ferreira",
                "phone": "(11) 98877-6655",
                "source": "Instagram",
                "development": "Vila dos Ipês",
                "broker": brokers[1],
                "objective": "moradia",
                "entry": "R$ 120.000 - R$ 150.000",
                "installment": "Até R$ 3.500",
                "timeline": "Agora / até 30 dias",
                "temperature": "quente",
                "score": 92,
                "status": "novo",
                "objection": "Posição do lote / incidência de sol",
                "next_action": "Ligar hoje às 16:00 para agendar visita e reforçar diferenciais da posição.",
                "days": 0,
            },
            {
                "name": "Mariana Costa",
                "phone": "(11) 97654-3321",
                "source": "Indicação",
                "development": "Solar das Árvores",
                "broker": brokers[2],
                "objective": "construção futura",
                "entry": "R$ 60.000",
                "installment": "Até R$ 2.800",
                "timeline": "Até 90 dias",
                "temperature": "quente",
                "score": 88,
                "status": "qualificado",
                "objection": "Preço um pouco alto",
                "next_action": "Enviar simulação personalizada e convite para visita ao decorado.",
                "days": 1,
            },
            {
                "name": "Fernando Almeida",
                "phone": "(11) 96421-0099",
                "source": "Plantão",
                "development": "Vila dos Ipês",
                "broker": brokers[3],
                "objective": "investimento",
                "entry": "R$ 80.000",
                "installment": "Até R$ 3.000",
                "timeline": "Este mês",
                "temperature": "quente",
                "score": 85,
                "status": "visita agendada",
                "objection": "Quer comparar valorização da região",
                "next_action": "Enviar mapa de localização, lote com maior liquidez e argumento de valorização.",
                "days": 2,
            },
            {
                "name": "Patrícia Santana",
                "phone": "(11) 94213-7788",
                "source": "Site",
                "development": "Reserva do Vale",
                "broker": brokers[0],
                "objective": "moradia",
                "entry": "R$ 35.000",
                "installment": "Até R$ 1.900",
                "timeline": "Até 60 dias",
                "temperature": "morno",
                "score": 78,
                "status": "proposta",
                "objection": "Entrada",
                "next_action": "Enviar materiais e simulação com entrada menor.",
                "days": 1,
            },
            {
                "name": "Rogério Martins",
                "phone": "(11) 93455-6677",
                "source": "Indicação",
                "development": "Solar das Árvores",
                "broker": brokers[1],
                "objective": "investimento",
                "entry": "R$ 25.000",
                "installment": "Até R$ 1.500",
                "timeline": "Sem pressa",
                "temperature": "morno",
                "score": 72,
                "status": "contato feito",
                "objection": "Precisa falar com a esposa",
                "next_action": "Enviar apresentação curta e perguntar melhor horário para conversar com ambos.",
                "days": 3,
            },
            {
                "name": "Letícia Andrade",
                "phone": "(11) 91234-5566",
                "source": "Instagram",
                "development": "Vila dos Ipês",
                "broker": brokers[2],
                "objective": "moradia",
                "entry": "R$ 20.000",
                "installment": "Até R$ 1.300",
                "timeline": "Até 6 meses",
                "temperature": "morno",
                "score": 67,
                "status": "qualificado",
                "objection": "Parcela",
                "next_action": "Qualificar renda e apresentar lote compatível antes de mandar tabela completa.",
                "days": 4,
            },
            {
                "name": "Gabriel Oliveira",
                "phone": "(11) 99876-4433",
                "source": "Plantão",
                "development": "Reserva do Vale",
                "broker": brokers[3],
                "objective": "indefinido",
                "entry": None,
                "installment": None,
                "timeline": "Indefinido",
                "temperature": "frio",
                "score": 61,
                "status": "novo",
                "objection": "Só pediu tabela",
                "next_action": "Fazer pergunta de diagnóstico antes de enviar tabela.",
                "days": 5,
            },
            {
                "name": "Thais Souza",
                "phone": "(11) 95566-2211",
                "source": "Site",
                "development": "Solar das Árvores",
                "broker": brokers[0],
                "objective": "construção futura",
                "entry": None,
                "installment": "Até R$ 1.100",
                "timeline": "Ano que vem",
                "temperature": "frio",
                "score": 59,
                "status": "nutrição",
                "objection": "Quer entender documentação",
                "next_action": "Enviar FAQ documental e vídeo institucional para nutrição.",
                "days": 6,
            },
        ]
        for idx, row in enumerate(lead_rows):
            created = now - timedelta(days=row["days"], hours=idx)
            lead = Lead(
                name=row["name"],
                phone=row["phone"],
                source=row["source"],
                development_id=developments[row["development"]].id,
                broker_id=row["broker"].id,
                objective=row["objective"],
                budget_entry=row["entry"],
                budget_installment=row["installment"],
                purchase_timeline=row["timeline"],
                knows_development=row["days"] % 2 == 0,
                temperature=row["temperature"],
                score=row["score"],
                status=row["status"],
                main_objection=row["objection"],
                next_action=row["next_action"],
                created_at=created,
                updated_at=created + timedelta(hours=2),
            )
            db.add(lead)
            db.flush()
            db.add_all(
                [
                    Interaction(
                        lead_id=lead.id,
                        broker_id=lead.broker_id,
                        direction="inbound",
                        channel="whatsapp_simulado",
                        message=f"Lead demonstrou interesse em {row['development']} via {row['source']}.",
                        summary="Interação simulada para demonstração.",
                        created_at=created + timedelta(minutes=15),
                    ),
                    Interaction(
                        lead_id=lead.id,
                        broker_id=lead.broker_id,
                        direction="system",
                        channel="leadflow",
                        message="Vitória classificou o lead e sugeriu próxima ação.",
                        summary="Classificação automática simulada.",
                        created_at=created + timedelta(minutes=20),
                    ),
                    LeadRecommendation(
                        lead_id=lead.id,
                        recommendation_type="estrategia",
                        diagnosis=f"Lead com perfil de {row['objective']} e temperatura {row['temperature']}.",
                        strategy=row["next_action"],
                        script=(
                            f"Oi, {row['name'].split()[0]}! Separei uma condição personalizada para você. "
                            "Posso te mostrar duas opções de lote e explicar qual delas faz mais sentido pelo seu perfil?"
                        ),
                        materials=["Mapa de localização", "Implantação geral", "Vídeo aéreo — Vista geral"],
                        created_at=created + timedelta(minutes=25),
                    ),
                    Task(
                        lead_id=lead.id,
                        broker_id=lead.broker_id,
                        task_type="follow_up",
                        description=row["next_action"],
                        due_at=now + timedelta(hours=idx + 2),
                        status="aberta",
                        created_at=created + timedelta(minutes=30),
                    ),
                ]
            )
        db.commit()

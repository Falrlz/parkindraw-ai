import React from 'react';
import { ArrowRight, Activity, CheckCircle2 } from 'lucide-react';
import { useRoute } from '../app/AppRouter';
import { homeContent } from '../content/home.content';
import { faqContent } from '../content/faq.content';
import { Button } from '../components/ui/Button';
import { Card, CardBody } from '../components/ui/Card';
import { SectionContainer } from '../components/shared/SectionContainer';
import { FaqItem } from '../features/faq/components/FaqItem';

export const HomePage: React.FC = () => {
  const { navigate } = useRoute();
  const { hero, explanation, workflow, biomarkers, ctaBanner } = homeContent;

  return (
    <div>
      {/* 1. Hero Section */}
      <section className="py-20 sm:py-28 text-center bg-white border-b border-slate-200">
        <SectionContainer>
          <div className="max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-slate-900 tracking-tight leading-tight">
              {hero.title}
            </h1>
            <p className="mt-3 text-xl sm:text-2xl md:text-3xl font-bold text-teal-700 font-mono tracking-tight">
              {hero.tagline}
            </p>
          </div>
        </SectionContainer>
      </section>

      {/* 2. Penjelasan ParkinDraw */}
      <section className="py-16 sm:py-20 bg-slate-50 border-b border-slate-200">
        <SectionContainer>
          <div className="max-w-3xl mx-auto text-center">
            <p className="text-base sm:text-lg md:text-xl text-slate-700 leading-relaxed font-normal">
              {explanation.text}
            </p>
          </div>
        </SectionContainer>
      </section>

      {/* 3. Workflow Section (01. Gambar -> 02. Analisis -> 03. Hasil) */}
      <div className="bg-slate-100/60 border-b border-slate-200">
        <SectionContainer>
          <header className="text-center max-w-2xl mx-auto mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              {workflow.heading}
            </h2>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {workflow.steps.map((step) => (
              <Card key={step.number} className="bg-white border-slate-200">
                <CardBody className="p-6">
                  <span className="text-3xl font-black text-teal-800/80 font-mono block mb-3">
                    {step.number}
                  </span>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{step.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    {step.description}
                  </p>
                </CardBody>
              </Card>
            ))}
          </div>
        </SectionContainer>
      </div>

      {/* 4. Biomarkers Section (Tiga Pola. Punya Cerita.) */}
      <SectionContainer>
        <header className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
            {biomarkers.heading}
          </h2>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {biomarkers.items.map((item) => (
            <Card key={item.id} className="border-slate-200">
              <CardBody className="p-6 flex flex-col h-full">
                <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 mb-4" aria-hidden="true">
                  <Activity className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{item.name}</h3>
                <p className="text-sm text-slate-600 leading-relaxed flex-1">
                  {item.description}
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      </SectionContainer>

      {/* 5. FAQ Section (Pertanyaan yang Sering Diajukan) */}
      <div className="bg-slate-100/50 border-t border-slate-200">
        <SectionContainer>
          <header className="text-center max-w-2xl mx-auto mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              {faqContent.heading}
            </h2>
          </header>

          <div className="max-w-2xl mx-auto space-y-3">
            {faqContent.items.map((faq) => (
              <FaqItem key={faq.id} item={faq} />
            ))}
          </div>
        </SectionContainer>
      </div>

      {/* 6. CTA Banner Section */}
      <div className="border-t border-slate-200 bg-white">
        <SectionContainer className="text-center py-12 sm:py-16">
          <div className="max-w-2xl mx-auto">
            <div className="w-12 h-12 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 mx-auto mb-4" aria-hidden="true">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-3">
              {ctaBanner.heading}
            </h2>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed mb-6">
              {ctaBanner.description}
            </p>
            <Button
              type="button"
              size="lg"
              onClick={() => navigate('/screening')}
              rightIcon={<ArrowRight className="w-5 h-5" />}
            >
              {ctaBanner.buttonText}
            </Button>
          </div>
        </SectionContainer>
      </div>
    </div>
  );
};

import React from 'react';
import { ArrowRight, BookOpen, Activity, CheckCircle2, ChevronRight } from 'lucide-react';
import { useRoute } from '../app/AppRouter';
import { homeContent } from '../content/home.content';
import { faqContent } from '../content/faq.content';
import { Button } from '../components/ui/Button';
import { Card, CardBody } from '../components/ui/Card';
import { SectionContainer } from '../components/shared/SectionContainer';
import { FaqItem } from '../features/faq/components/FaqItem';

export const HomePage: React.FC = () => {
  const { navigate } = useRoute();
  const { hero, workflow, biomarkers, faqPreview, ctaBanner } = homeContent;

  // Take top 3 FAQ questions for preview
  const previewFaqs = faqContent.categories.flatMap((cat) => cat.items).slice(0, 3);

  return (
    <div>
      {/* 1. Hero Section */}
      <SectionContainer className="pt-12 sm:pt-16 pb-12 text-center">
        <div className="max-w-3xl mx-auto">
          <p className="text-xs font-bold uppercase tracking-wider text-teal-800 bg-teal-50 border border-teal-200 inline-block px-3 py-1 rounded-full mb-4">
            {hero.badge}
          </p>

          <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
            {hero.title}
            <span className="block text-xl sm:text-2xl font-bold text-teal-700 mt-2 font-mono">
              {hero.tagline}
            </span>
          </h1>

          <p className="mt-5 text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
            {hero.lead}
          </p>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button
              type="button"
              size="lg"
              onClick={() => navigate('/screening')}
              rightIcon={<ArrowRight className="w-5 h-5" />}
              className="w-full sm:w-auto"
            >
              {hero.primaryCta}
            </Button>

            <Button
              type="button"
              size="lg"
              variant="outline"
              onClick={() => navigate('/about')}
              leftIcon={<BookOpen className="w-4 h-4" />}
              className="w-full sm:w-auto"
            >
              {hero.secondaryCta}
            </Button>
          </div>
        </div>
      </SectionContainer>

      {/* 2. Workflow Section (01. Gambar -> 02. Analisis -> 03. Hasil) */}
      <div className="bg-slate-100/60 border-y border-slate-200">
        <SectionContainer>
          <header className="text-center max-w-2xl mx-auto mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              {workflow.heading}
            </h2>
            <p className="mt-2 text-sm sm:text-base text-slate-600">
              {workflow.subtitle}
            </p>
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

      {/* 3. Biomarkers Section (Tiga Pola. Punya Cerita.) */}
      <SectionContainer>
        <header className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
            {biomarkers.heading}
          </h2>
          <p className="mt-2 text-sm sm:text-base text-slate-600">
            {biomarkers.subtitle}
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {biomarkers.items.map((item) => (
            <Card key={item.id} className="border-slate-200">
              <CardBody className="p-6 flex flex-col h-full">
                <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 mb-4" aria-hidden="true">
                  <Activity className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  {item.category}
                </span>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{item.name}</h3>
                <p className="text-sm text-slate-600 leading-relaxed flex-1">
                  {item.description}
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      </SectionContainer>

      {/* 4. FAQ Preview Section */}
      <div className="bg-slate-100/50 border-t border-slate-200">
        <SectionContainer>
          <header className="text-center max-w-2xl mx-auto mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              {faqPreview.heading}
            </h2>
            <p className="mt-2 text-sm sm:text-base text-slate-600">
              {faqPreview.subtitle}
            </p>
          </header>

          <div className="max-w-2xl mx-auto space-y-3 mb-6">
            {previewFaqs.map((faq) => (
              <FaqItem key={faq.id} item={faq} />
            ))}
          </div>

          <div className="text-center">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/faq')}
              rightIcon={<ChevronRight className="w-4 h-4" />}
            >
              {faqPreview.seeAllCta}
            </Button>
          </div>
        </SectionContainer>
      </div>

      {/* 5. CTA Banner Section */}
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

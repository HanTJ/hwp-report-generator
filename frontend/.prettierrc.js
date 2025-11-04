export default {
    singleQuote: true, // 싱글 쿼트 사용 여부
    semi: false, // 세미 콜론 무조건 적용 여부(false 인 경우 오류 발생 할 소지가 있으면 세미 콜론 추가 됨)
    trailingComma: 'none', // 끝에 콤마 허용 안함
    printWidth: 150, // 줄바꿈 처리 기준 넓이
    useTabs: false, // 탭 사용 여부 false 면 탭은 tabWidth 만큼 공백으로 치환
    tabWidth: 4, // 탭 넓이
    arrowParens: 'always', // 화살표 함수 파라미터 없을때 괄호 사용 여부
    singleAttributePerLine: false, // 한 줄에 하나의 속성 적용 여부
    jsxSingleQuote: false, // JSX 요소 싱글 쿼트 사용 여부
    bracketSpacing: false, // 객체 {} 리터럴 대괄호 공백 허용 여부
    bracketSameLine: true //JSX 요소의 를 다음 줄에 단독으로 두는 대신 마지막 줄 끝에 넣음
}
